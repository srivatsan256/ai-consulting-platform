import React from "react";
import LegalDocument from "../../components/LegalDocument";
import "./PrivacyPolicyPage.css";

const P = ({ children }) => <p className="privacy-p">{children}</p>;

const UL = ({ items }) => (
  <ul className="privacy-ul">
    {items.map((item, idx) => (
      <li key={idx}>{item}</li>
    ))}
  </ul>
);

const QuoteBox = ({ children }) => (
  <div className="privacy-quote">
    <p className="privacy-quote-text">{children}</p>
  </div>
);

const ContactBox = ({ items }) => (
  <div className="privacy-contact">
    {items.map(([label, value]) => (
      <p key={label}>
        <span className="privacy-contact-label">
          {label}:
        </span>
        <span className="privacy-contact-value">{value}</span>
      </p>
    ))}
  </div>
);

export default function PrivacyPolicyPage() {
  const sections = [
    {
      id: "introduction",
      title: "Introduction",
      body: (
        <>
          <P>
            Welcome to Synthetix Enterprise. This Privacy Policy outlines our practices regarding the
            collection, use, and disclosure of your information when you use our services. We respect
            your privacy and are committed to protecting it through our compliance with this policy.
          </P>
          <P>
            This policy applies to information we collect across all our digital platforms, including
            our website, mobile applications, and any AI-driven enterprise tools we provide. Please
            read this policy carefully to understand our policies and practices regarding your
            information and how we will treat it.
          </P>
        </>
      ),
    },
    {
      id: "information-collection",
      title: "Information Collection",
      body: (
        <>
          <P>We collect several types of information from and about users of our Services, including:</P>
          <UL
            items={[
              <>
                <strong>Personal Information:</strong> Name, postal address, e-mail address, telephone
                number, or any other identifier by which you may be contacted online or offline.
              </>,
              <>
                <strong>Usage Data:</strong> Details of your visits to our Website, including traffic
                data, location data, logs, and other communication data and the resources that you
                access and use on the Website.
              </>,
              <>
                <strong>Device Information:</strong> Information about your computer and internet
                connection, including your IP address, operating system, and browser type.
              </>,
            ]}
          />
        </>
      ),
    },
    {
      id: "usage",
      title: "Usage",
      body: (
        <>
          <P>We use information that we collect about you or that you provide to us, including any personal information:</P>
          <UL
            items={[
              "To present our Services and its contents to you in a highly optimized format.",
              "To provide you with information, products, or services that you request from us.",
              "To fulfill any other purpose for which you provide it.",
              "To carry out our obligations and enforce our rights arising from any contracts entered into between you and us, including for billing and collection.",
              "To notify you about changes to our Services or any products or services we offer or provide though it.",
            ]}
          />
        </>
      ),
    },
    {
      id: "cookies",
      title: "Cookies",
      body: (
        <P>
          We use cookies and similar tracking technologies to track the activity on our Service and
          hold certain information. Cookies are files with a small amount of data which may include an
          anonymous unique identifier. You can instruct your browser to refuse all cookies or to
          indicate when a cookie is being sent. However, if you do not accept cookies, you may not be
          able to use some portions of our Service.
        </P>
      ),
    },
    {
      id: "storage",
      title: "Storage",
      body: (
        <P>
          We will retain your Personal Data only for as long as is necessary for the purposes set out
          in this Privacy Policy. We will retain and use your Personal Data to the extent necessary to
          comply with our legal obligations (for example, if we are required to retain your data to
          comply with applicable laws), resolve disputes, and enforce our legal agreements and
          policies.
        </P>
      ),
    },
    {
      id: "security",
      title: "Security",
      body: (
        <>
          <QuoteBox>
            "The security of your data is paramount. We implement enterprise-grade encryption and
            access controls across all operational layers."
          </QuoteBox>
          <P>
            The security of your data is important to us, but remember that no method of transmission
            over the Internet, or method of electronic storage is 100% secure. While we strive to use
            commercially acceptable means to protect your Personal Data, we cannot guarantee its
            absolute security. We utilize advanced cryptographic standards and continuous monitoring
            to mitigate risks.
          </P>
        </>
      ),
    },
    {
      id: "third-party-services",
      title: "Third-Party Services",
      body: (
        <P>
          We may employ third party companies and individuals to facilitate our Service ("Service
          Providers"), to provide the Service on our behalf, to perform Service-related services, or
          to assist us in analyzing how our Service is used. These third parties have access to your
          Personal Data only to perform these tasks on our behalf and are obligated not to disclose or
          use it for any other purpose.
        </P>
      ),
    },
    {
      id: "user-rights",
      title: "User Rights",
      body: (
        <P>
          You have certain data protection rights. We aim to take reasonable steps to allow you to
          correct, amend, delete, or limit the use of your Personal Data. If you wish to be informed
          what Personal Data we hold about you and if you want it to be removed from our systems,
          please contact us.
        </P>
      ),
    },
    {
      id: "updates",
      title: "Updates",
      body: (
        <P>
          We may update our Privacy Policy from time to time. We will notify you of any changes by
          posting the new Privacy Policy on this page. We will let you know via email and/or a
          prominent notice on our Service, prior to the change becoming effective and update the
          "effective date" at the top of this Privacy Policy.
        </P>
      ),
    },
    {
      id: "contact-info",
      title: "Contact Info",
      body: (
        <>
          <P>If you have any questions about this Privacy Policy, please contact us:</P>
          <ContactBox
            items={[
              ["By email", "privacy@synthetix.enterprise"],
              ["By phone", "+1 (555) 012-3456"],
              ["By mail", "100 Innovation Way, Suite 400, Tech District"],
            ]}
          />
        </>
      ),
    },
  ];

  return (
    <LegalDocument
      eyebrow="Legal Document"
      title="Privacy Policy"
      lastUpdated="October 26, 2023"
      sections={sections}
      withToc
    />
  );
}
