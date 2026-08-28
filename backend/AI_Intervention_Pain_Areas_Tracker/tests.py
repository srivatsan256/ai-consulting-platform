import io

from django.db import connection
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import AIInterventionPainArea

TEST_TABLE_SQL = """
CREATE TABLE ai_intervention_pain_areas_tracker (
    id               SERIAL PRIMARY KEY,
    date             DATE NOT NULL,
    department       VARCHAR(255) NOT NULL DEFAULT '',
    process_activity VARCHAR(255) NOT NULL DEFAULT '',
    pain_area        TEXT NOT NULL DEFAULT '',
    current_method   TEXT NOT NULL DEFAULT '',
    frequency        VARCHAR(100) NOT NULL DEFAULT '',
    time_spent_hrs   DOUBLE PRECISION NULL,
    impact_area      VARCHAR(255) NOT NULL DEFAULT '',
    ai_intervention  TEXT NOT NULL DEFAULT '',
    expected_benefit TEXT NOT NULL DEFAULT '',
    priority         VARCHAR(20) NOT NULL DEFAULT 'Medium',
    feasibility      VARCHAR(20) NOT NULL DEFAULT 'Medium',
    owner            VARCHAR(255) NOT NULL DEFAULT '',
    target_date      DATE NULL,
    status           VARCHAR(20) NOT NULL DEFAULT 'Open',
    remarks          TEXT NOT NULL DEFAULT '',
    impact_score     INTEGER GENERATED ALWAYS AS (
        CASE WHEN time_spent_hrs IS NULL THEN 1
             WHEN time_spent_hrs >= 40 THEN 3
             WHEN time_spent_hrs >= 10 THEN 2
             ELSE 1 END
    ) STORED,
    feasibility_score INTEGER GENERATED ALWAYS AS (
        CASE feasibility WHEN 'High' THEN 3 WHEN 'Medium' THEN 2 ELSE 1 END
    ) STORED,
    priority_score    INTEGER GENERATED ALWAYS AS (
        CASE priority WHEN 'High' THEN 3 WHEN 'Medium' THEN 2 ELSE 1 END
    ) STORED,
    quadrant          VARCHAR(30) GENERATED ALWAYS AS (
        CASE WHEN (CASE WHEN time_spent_hrs IS NULL THEN 1 WHEN time_spent_hrs >= 40 THEN 3 WHEN time_spent_hrs >= 10 THEN 2 ELSE 1 END) >= 2
                  AND (CASE feasibility WHEN 'High' THEN 3 WHEN 'Medium' THEN 2 ELSE 1 END) >= 2 THEN 'Quick Win'
             WHEN (CASE WHEN time_spent_hrs IS NULL THEN 1 WHEN time_spent_hrs >= 40 THEN 3 WHEN time_spent_hrs >= 10 THEN 2 ELSE 1 END) >= 2 THEN 'Strategic'
             WHEN (CASE feasibility WHEN 'High' THEN 3 WHEN 'Medium' THEN 2 ELSE 1 END) >= 2 THEN 'Fill In'
             ELSE 'Revisit' END
    ) STORED,
    created_at       TIMESTAMP NOT NULL,
    updated_at       TIMESTAMP NOT NULL
)
"""


class PainAreaCSVUploadTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The table is unmanaged (created via raw SQL in production), so the
        # test database needs it created explicitly.
        with connection.cursor() as cursor:
            cursor.execute(TEST_TABLE_SQL)

    def setUp(self):
        self.user = self._make_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.upload_url = reverse("pain-area-upload-csv")

    def _make_user(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.create_user(
            email="csv.tester@example.com",
            username="csvtester",
            password="testpass123",
        )

    def _upload(self, csv_text, name="upload.csv"):
        payload = {"file": io.BytesIO(csv_text.encode("utf-8-sig"))}
        payload["file"].name = name
        response = self.client.post(self.upload_url, payload, format="multipart")
        return response

    def _fields(self):
        return (
            "date,department,process_activity,pain_area,current_method,frequency,"
            "time_spent_hrs,impact_area,ai_intervention,expected_benefit,"
            "priority,feasibility,owner,target_date,status,remarks"
        )

    def test_iso_csv_imports(self):
        csv_text = "\n".join(
            [
                self._fields(),
                "2026-08-01,IT,Manual data entry,Report errors,Manually copying,2,"
                "1.5,Operational,Automated extraction,Saves 2 hrs/week,"
                "High,High,Alice,,Open,None",
            ]
        )
        response = self._upload(csv_text)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["inserted"], 1)
        self.assertEqual(response.data["skipped"], 0)
        self.assertTrue(AIInterventionPainArea.objects.filter(pain_area="Report errors").exists())

    def test_master_tracker_headers_import(self):
        header = (
            "Sl. No.,Date,Department,Process / Activity,Pain Area / Problem Statement,"
            "Current Method,Frequency,Time Spent / Month (Hrs),Impact Area,"
            "AI Intervention Required,Expected Benefit,Priority,Feasibility,Owner,"
            "Target Date,Status,Remarks,impact_score,feasibility_score,priority_score,quadrant"
        )
        csv_text = "\n".join(
            [
                header,
                "1,13/08/2026,IT,Manual data entry,Pain Area / Problem Statement example,"
                "Typing,3,60,Operational,AI Intervention Required example,"
                "Saves time,High,Medium,Bob,20/09/2026,Open,None,3,2,3,Quick Win",
            ]
        )
        response = self._upload(csv_text)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["inserted"], 1, response.data)
        self.assertEqual(response.data["skipped"], 0, response.data["warnings"])
        row = AIInterventionPainArea.objects.get(pain_area="Pain Area / Problem Statement example")
        self.assertEqual(row.process_activity, "Manual data entry")
        self.assertEqual(row.time_spent_hrs, 60)
        self.assertEqual(row.ai_intervention, "AI Intervention Required example")
        self.assertEqual(row.date.isoformat(), "2026-08-13")

    def test_two_digit_year_dates_import(self):
        header = (
            "#\tdate\tdepartment\tprocess_activity\tpain_area\tcurrent_method\t"
            "frequency\ttime_spent_hrs\timpact_area\tai_intervention\t"
            "expected_benefit\tpriority\tfeasibility\towner\ttarget_date\tstatus\tremarks"
        )
        rows = [
            "1\t13/08/26\tOperations\tInvoice Processing\tManual data entry takes 3+ hours per day\t"
            "Manual entry into spreadsheets\tDaily\t3\tSpeed, Cost\tAutomated invoice data extraction\t"
            "Save ~50 hours per month\tHigh\tHigh\tJane Doe\t01/10/26\tOpen\tPrioritize before month-end close",
            "2\t13/08/26\tFinance\tExpense Verification\tManual checking of expense claims\t"
            "Spreadsheet review\tDaily\t2.5\tAccuracy, Speed\tAI expense validation\t"
            "Reduce verification time by 60%\tHigh\tHigh\tRobert Smith\t20/09/26\tOpen\tFrequent duplicate claims",
            "3\t13/08/26\tHR\tResume Screening\tLarge number of resumes require manual review\t"
            "Manual resume screening\tWeekly\t5\tSpeed, Productivity\tAI resume ranking\t"
            "Reduce screening effort by 70%\tHigh\tHigh\tPriya Kumar\t15/09/26\tIn Progress\tRecruitment volume increasing",
        ]
        response = self._upload("\n".join([header, *rows]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["inserted"], 3, response.data)
        self.assertEqual(response.data["skipped"], 0, response.data["warnings"])
        invoice = AIInterventionPainArea.objects.get(process_activity="Invoice Processing")
        self.assertEqual(invoice.date.isoformat(), "2026-08-13")
        self.assertEqual(invoice.target_date.isoformat(), "2026-10-01")
        self.assertEqual(invoice.pain_area, "Manual data entry takes 3+ hours per day")
        self.assertEqual(invoice.impact_area, "Speed, Cost")
        self.assertEqual(AIInterventionPainArea.objects.filter(date="2026-08-13").count(), 3)

    def test_two_digit_year_dates_comma_delimited(self):
        header = (
            "#,date,department,process_activity,pain_area,current_method,"
            "frequency,time_spent_hrs,impact_area,ai_intervention,"
            "expected_benefit,priority,feasibility,owner,target_date,status,remarks"
        )
        row = (
            "1,13/08/26,Operations,Invoice Processing,Pain area text,"
            "Manual entry,Daily,3,Speed and Cost,AI extraction,"
            "Saves time,High,High,Jane Doe,01/10/26,Open,None"
        )
        response = self._upload("\n".join([header, row]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["inserted"], 1, response.data)
        self.assertEqual(response.data["skipped"], 0, response.data["warnings"])
        rec = AIInterventionPainArea.objects.get(process_activity="Invoice Processing")
        self.assertEqual(rec.date.isoformat(), "2026-08-13")

    def test_excel_dd_mm_yyyy_dates_import(self):
        csv_text = "\n".join(
            [
                self._fields(),
                "13/08/2026,IT,Manual data entry,Excel date error,Typing data,3,"
                "2,Operational,Automated extraction,Saves 2 hrs/week,"
                "High,Medium,Bob,20/09/2026,Open,None",
            ]
        )
        response = self._upload(csv_text)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["inserted"], 1, response.data)
        row = AIInterventionPainArea.objects.get(pain_area="Excel date error")
        self.assertEqual(row.date.isoformat(), "2026-08-13")
        self.assertEqual(row.target_date.isoformat(), "2026-09-20")

    def test_semicolon_delimited_excel_export(self):
        rows = [
            self._fields().replace(",", ";"),
            "13/08/2026;IT;Manual data entry;Semicolon file;Typing;3;"
            "2;Operational;Automated extraction;Saves time;"
            "High;Medium;Bob;20/09/2026;Open;None",
        ]
        response = self._upload("\n".join(rows))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["inserted"], 1, response.data)
        self.assertTrue(AIInterventionPainArea.objects.filter(pain_area="Semicolon file").exists())

    def test_spaced_title_case_headers(self):
        header = (
            "Date,Department,Process Activity,Pain Area,Current Method,Frequency,"
            "Time Spent (hrs),Impact Area,AI Intervention,Expected Benefit,"
            "Priority,Feasibility,Owner,Target Date,Status,Remarks"
        )
        csv_text = "\n".join(
            [
                header,
                "13/08/2026,IT,Manual entry,Spaced headers,Typing,3,"
                "2,Operational,Automated,Saves time,"
                "High,Medium,Bob,20/09/2026,Open,None",
            ]
        )
        response = self._upload(csv_text)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["inserted"], 1, response.data)
        self.assertTrue(AIInterventionPainArea.objects.filter(pain_area="Spaced headers").exists())

    def test_excel_serial_date_numbers(self):
        serial = 45800  # 2025-05-23
        csv_text = "\n".join(
            [
                self._fields(),
                f"{serial},IT,Manual entry,Serial date,Typing,3,"
                "2,Operational,Automated,Saves time,"
                "High,Medium,Bob,,Open,None",
            ]
        )
        response = self._upload(csv_text)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["inserted"], 1, response.data)
        row = AIInterventionPainArea.objects.get(pain_area="Serial date")
        self.assertEqual(row.date.isoformat(), "2025-05-23")

    def test_invalid_dates_are_skipped_with_warnings(self):
        csv_text = "\n".join(
            [
                self._fields(),
                "not-a-date,IT,Manual entry,Bad row,Typing,3,"
                "2,Operational,Automated,Saves time,"
                "High,Medium,Bob,,Open,None",
            ]
        )
        response = self._upload(csv_text)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["inserted"], 0)
        self.assertEqual(response.data["skipped"], 1)
        self.assertEqual(len(response.data["warnings"]), 1)

    def test_unrecognized_headers_return_400(self):
        csv_text = "\n".join(
            [
                "foo,bar,baz",
                "1,2,3",
            ]
        )
        response = self._upload(csv_text)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no data rows", response.data["detail"].lower())

    def test_calculated_fields_high_impact_quick_win(self):
        row = AIInterventionPainArea.objects.create(
            date="2026-08-01",
            process_activity="Invoice processing",
            time_spent_hrs=60,
            priority="High",
            feasibility="High",
        )
        impact_score, feasibility_score, priority_score, quadrant = self._read_calculated(row.id)
        self.assertEqual((impact_score, feasibility_score, priority_score, quadrant), (3, 3, 3, "Quick Win"))

    def test_calculated_fields_low_impact_revisit(self):
        row = AIInterventionPainArea.objects.create(
            date="2026-08-01",
            process_activity="Report formatting",
            time_spent_hrs=2,
            priority="Low",
            feasibility="Low",
        )
        impact_score, feasibility_score, priority_score, quadrant = self._read_calculated(row.id)
        self.assertEqual((impact_score, feasibility_score, priority_score, quadrant), (1, 1, 1, "Revisit"))

    def test_calculated_fields_null_hours_fill_in(self):
        row = AIInterventionPainArea.objects.create(
            date="2026-08-01",
            process_activity="Archive search",
            time_spent_hrs=None,
            priority="Medium",
            feasibility="High",
        )
        impact_score, feasibility_score, priority_score, quadrant = self._read_calculated(row.id)
        self.assertEqual((impact_score, feasibility_score, priority_score, quadrant), (1, 3, 2, "Fill In"))

    def test_api_exposes_calculated_fields_read_only(self):
        payload = {
            "date": "2026-08-01",
            "process_activity": "Expense verification",
            "time_spent_hrs": 25,
            "priority": "Medium",
            "feasibility": "High",
        }
        response = self.client.post(reverse("pain-area-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        record_id = response.data["id"]
        self.assertEqual(response.data["impact_score"], 2)
        self.assertEqual(response.data["feasibility_score"], 3)
        self.assertEqual(response.data["priority_score"], 2)
        self.assertEqual(response.data["total_score"], 7)
        self.assertEqual(response.data["quadrant"], "Quick Win")

        detail = self.client.get(reverse("pain-area-detail", args=[record_id]), format="json")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["quadrant"], "Quick Win")

    def _read_calculated(self, record_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT impact_score, feasibility_score, priority_score, quadrant "
                "FROM ai_intervention_pain_areas_tracker WHERE id = %s",
                [record_id],
            )
            return cursor.fetchone()


class PainAreaRecommendationTests(TestCase):
    """Module 4.1-4.3: recommendation engine, confidence and reasoning."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as cursor:
            cursor.execute(TEST_TABLE_SQL)

    def setUp(self):
        self.client = APIClient()
        self.user = self._make_user()
        self.client.force_authenticate(user=self.user)

    def _make_user(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.create_user(
            email="rec.tester@example.com",
            username="rectester",
            password="testpass123",
        )

    def _create(self, **kwargs):
        defaults = {
            "date": "2026-08-01",
            "process_activity": "Invoice processing",
            "pain_area": "Staff manually type invoice data into the ERP",
            "current_method": "Manual data entry and copying",
            "time_spent_hrs": 60,
            "priority": "High",
            "feasibility": "High",
        }
        defaults.update(kwargs)
        return AIInterventionPainArea.objects.create(**defaults)

    def test_api_exposes_recommendation_fields(self):
        record = self._create()
        response = self.client.get(
            reverse("pain-area-detail", args=[record.id]), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["ai_recommendation"], "Workflow Automation")
        self.assertEqual(data["ai_recommendation_key"], "workflow_automation")
        self.assertGreaterEqual(data["ai_confidence"], 55)
        self.assertLessEqual(data["ai_confidence"], 98)
        self.assertIn("hours per month", data["ai_reasoning"])
        self.assertIn("Workflow Automation", data["ai_reasoning"])

    def test_recommendation_examples(self):
        cases = [
            (
                {
                    "process_activity": "Customer support",
                    "pain_area": "Agents answer repetitive customer queries via chat",
                    "current_method": "Manual chat and email replies",
                    "ai_intervention": "Chatbot",
                    "time_spent_hrs": 40,
                },
                "Conversational AI",
            ),
            (
                {
                    "process_activity": "Report generation",
                    "pain_area": "Analysts hand-write monthly reports",
                    "current_method": "Writing reports in Word",
                    "ai_intervention": "Generate reports",
                    "time_spent_hrs": 45,
                },
                "Generative AI Assistant",
            ),
            (
                {
                    "process_activity": "Employee onboarding",
                    "pain_area": "New hires ask the same questions repeatedly",
                    "current_method": "Manual answers from scattered documents",
                    "ai_intervention": "Knowledge base",
                    "time_spent_hrs": 50,
                },
                "AI Knowledge Base",
            ),
            (
                {
                    "process_activity": "Compliance review",
                    "pain_area": "Team manually reviews contracts and PDFs",
                    "current_method": "Reading scanned documents",
                    "ai_intervention": "Extract from documents",
                    "time_spent_hrs": 50,
                },
                "Document Intelligence",
            ),
        ]
        for fields, expected in cases:
            record = self._create(**fields)
            response = self.client.get(
                reverse("pain-area-detail", args=[record.id]), format="json"
            )
            self.assertEqual(response.data["ai_recommendation"], expected)

    def test_reports_endpoint_lists_types(self):
        self._create()
        response = self.client.get(reverse("pain-area-reports"), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        keys = {r["key"] for r in response.data["report_types"]}
        self.assertEqual(
            keys,
            {
                "opportunity-assessment",
                "department-summary",
                "executive-summary",
                "adoption-roadmap",
                "opportunity-register",
            },
        )
        self.assertGreaterEqual(response.data["data"]["report_count"], 1)

    def test_export_pdf(self):
        self._create()
        url = reverse("pain-area-report-export", args=["executive-summary"])
        response = self.client.get(url, {"file_format": "pdf"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertIn("filename", response["Content-Disposition"])

    def test_export_xlsx(self):
        self._create()
        url = reverse("pain-area-report-export", args=["opportunity-register"])
        response = self.client.get(url, {"file_format": "xlsx"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "spreadsheetml",
            response["Content-Type"],
        )
        self.assertTrue(response.content[:2] == b"PK")

    def test_export_csv(self):
        self._create()
        url = reverse("pain-area-report-export", args=["opportunity-register"])
        response = self.client.get(url, {"file_format": "csv"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("filename", response["Content-Disposition"])

    def test_export_unknown_report_404(self):
        url = reverse("pain-area-report-export", args=["does-not-exist"])
        response = self.client.get(url, {"file_format": "pdf"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_export_invalid_format_400(self):
        url = reverse("pain-area-report-export", args=["executive-summary"])
        response = self.client.get(url, {"file_format": "docx"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
