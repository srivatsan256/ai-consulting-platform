import React from "react";
import LegalDocument from "../../components/LegalDocument";
import "../../styles/pages/marketing/TermsOfServicePage.css";

const Section = ({ heading, children }) => (
  <section>
    <h2 className="tos-section-h2">
      {heading}
    </h2>
    <div className="tos-section-body">{children}</div>
  </section>
);

const P = ({ children }) => <p>{children}</p>;

const UL = ({ items }) => (
  <ul className="tos-ul">
    {items.map((item, idx) => (
      <li key={idx}>{item}</li>
    ))}
  </ul>
);

export default function TermsOfServicePage() {
  return (
    <LegalDocument
      eyebrow="Legal Information"
      title="Terms of Service"
      lastUpdated="October 24, 2024"
      withToc={false}
      sections={[
        {
          id: "acceptance",
          title: "1. Acceptance of Terms",
          body: (
            <Section heading="1. Acceptance of Terms">
              <P>
                By accessing or using the Synthetix Enterprise platform ("the Service"), you agree to
                be bound by these Terms of Service. If you disagree with any part of the terms, you do
                not have permission to access the Service.
              </P>
              <P>
                These terms represent a legally binding agreement between you, either as an individual
                or on behalf of a corporate entity ("Customer"), and Synthetix Enterprise ("Company",
                "we", "us", or "our").
              </P>
            </Section>
          ),
        },
        {
          id: "user-accounts",
          title: "2. User Accounts",
          body: (
            <Section heading="2. User Accounts">
              <P>
                When you create an account with us, you must provide information that is accurate,
                complete, and current at all times. Failure to do so constitutes a breach of the Terms,
                which may result in immediate termination of your account.
              </P>
              <P>
                You are responsible for safeguarding the password that you use to access the Service
                and for any activities or actions under your password. You must notify us immediately
                upon becoming aware of any breach of security or unauthorized use of your account.
              </P>
            </Section>
          ),
        },
        {
          id: "billing",
          title: "3. Billing and Subscriptions",
          body: (
            <Section heading="3. Billing and Subscriptions">
              <P>
                Some parts of the Service are billed on a subscription basis. You will be billed in
                advance on a recurring and periodic basis (such as monthly or annually), depending on
                the type of subscription plan you select when purchasing a Subscription.
              </P>
              <P>
                At the end of each period, your Subscription will automatically renew under the exact
                same conditions unless you cancel it or Synthetix Enterprise cancels it. You may cancel
                your Subscription renewal either through your online account management page or by
                contacting our customer support team.
              </P>
            </Section>
          ),
        },
        {
          id: "acceptable-use",
          title: "4. Acceptable Use Policy",
          body: (
            <Section heading="4. Acceptable Use Policy">
              <P>
                You agree not to use the Service in any way that causes, or may cause, damage to the
                Service or impairment of the availability or accessibility of the Service, or in any
                way which is unlawful, illegal, fraudulent or harmful.
              </P>
              <UL
                items={[
                  "Do not reverse engineer, decompile, or disassemble the platform.",
                  "Do not use the platform to process sensitive personal data without proper authorization.",
                  "Do not attempt to circumvent any technical limitations or security measures embedded within the AI engines.",
                ]}
              />
            </Section>
          ),
        },
        {
          id: "intellectual-property",
          title: "5. Intellectual Property",
          body: (
            <Section heading="5. Intellectual Property">
              <P>
                The Service and its original content (excluding Content provided by you or other
                users), features and functionality are and will remain the exclusive property of
                Synthetix Enterprise and its licensors. The Service is protected by copyright,
                trademark, and other laws of both the United States and foreign countries.
              </P>
            </Section>
          ),
        },
        {
          id: "data-ownership",
          title: "6. Data Ownership",
          body: (
            <Section heading="6. Data Ownership">
              <P>
                You retain all of your ownership rights in your Data. By submitting Data to the
                Service, you grant us a worldwide, non-exclusive, royalty-free license strictly for
                the purpose of providing, maintaining, and improving the Service.
              </P>
              <P>
                Synthetix Enterprise does not use your proprietary customer data to train generalized
                AI models shared with other customers without your explicit opt-in consent.
              </P>
            </Section>
          ),
        },
        {
          id: "availability",
          title: "7. Service Availability",
          body: (
            <Section heading="7. Service Availability">
              <P>
                We strive to ensure a 99.9% uptime for the Service. However, the Service is provided
                on an "AS IS" and "AS AVAILABLE" basis. We reserve the right to suspend or withdraw
                the Service temporarily for maintenance or updates, provided we offer reasonable prior
                notice for scheduled downtime.
              </P>
            </Section>
          ),
        },
        {
          id: "liability",
          title: "8. Limitation of Liability",
          body: (
            <Section heading="8. Limitation of Liability">
              <P>
                In no event shall Synthetix Enterprise, nor its directors, employees, partners, agents,
                suppliers, or affiliates, be liable for any indirect, incidental, special,
                consequential or punitive damages, including without limitation, loss of profits, data,
                use, goodwill, or other intangible losses, resulting from (i) your access to or use of
                or inability to access or use the Service; (ii) any conduct or content of any third
                party on the Service.
              </P>
            </Section>
          ),
        },
        {
          id: "termination",
          title: "9. Termination",
          body: (
            <Section heading="9. Termination">
              <P>
                We may terminate or suspend your account and bar access to the Service immediately,
                without prior notice or liability, under our sole discretion, for any reason whatsoever
                and without limitation, including but not limited to a breach of the Terms.
              </P>
              <P>
                If you wish to terminate your account, you may simply discontinue using the Service or
                initiate account deletion from your settings dashboard.
              </P>
            </Section>
          ),
        },
        {
          id: "governing-law",
          title: "10. Governing Law",
          body: (
            <Section heading="10. Governing Law">
              <P>
                These Terms shall be governed and construed in accordance with the laws of Delaware,
                United States, without regard to its conflict of law provisions.
              </P>
              <P>
                Our failure to enforce any right or provision of these Terms will not be considered a
                waiver of those rights. If any provision of these Terms is held to be invalid or
                unenforceable by a court, the remaining provisions of these Terms will remain in
                effect.
              </P>
            </Section>
          ),
        },
      ]}
    />
  );
}
