import io

from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import AIInterventionPainArea


class PainAreaCSVUploadTests(TestCase):
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
        serial = 45800  # 2025-05-30
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
        self.assertEqual(row.date.isoformat(), "2025-05-30")

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
