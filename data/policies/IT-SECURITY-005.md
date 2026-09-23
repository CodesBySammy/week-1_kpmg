---
document_id: IT-SECURITY-005
title: Information Security and Acceptable Use Policy
category: IT & Security
policy_type: Security
version: "3.2"
effective_date: "2025-01-01"
department: Information Security
last_reviewed: "2025-08-10"
status: Active
---

# Information Security and Acceptable Use Policy

## 1. Overview and Purpose
This Information Security Policy defines guidelines and operational standards for protecting company information assets, computing infrastructure, network devices, intellectual property, and client data against unauthorized access, loss, or disclosure. All full-time employees, contractors, interns, and third-party vendors must comply with these standards.

## 2. Password and Authentication Requirements
### 2.1 Password Complexity Standards
All corporate user accounts must enforce the following password parameters:
- Minimum length of 14 alphanumeric characters.
- Must contain at least one uppercase letter (A-Z), one lowercase letter (a-z), one numeric digit (0-9), and one approved special symbol (!@#$%^&*).
- Passwords expire every 90 days. Users may not reuse any of the last 10 previous passwords.
- Account lockout occurs after 5 consecutive failed login attempts within 15 minutes. Locked accounts require IT Helpdesk verification or automated self-service MFA reset.

### 2.2 Multi-Factor Authentication (MFA)
- Multi-Factor Authentication (MFA) via corporate authenticator app or hardware FIDO2 key is mandatory for:
  - All Single Sign-On (SSO) portals.
  - Virtual Private Network (VPN) and remote desktop connections.
  - Cloud infrastructure consoles (AWS, Azure, GCP) and production database bastion hosts.
- SMS-based verification is strictly prohibited as a standalone secondary authentication method for production access.

## 3. Workstation and Device Security
### 3.1 Device Encryption and Antivirus
- All company-provided laptops and desktops must have full-disk encryption (BitLocker or FileVault) enabled with centralized key escrow.
- Corporate Endpoint Detection and Response (EDR) agent must be active, running real-time behavioral scanning, and updated within 24 hours.
- Operating system security patches must be installed within 14 calendar days of public release. Critical zero-day vulnerabilities must be patched within 48 hours.

### 3.2 Screen Lock and Clean Desk Policy
- Workstations must automatically lock after 5 minutes of user inactivity.
- Users must manually lock workstations (Win+L / Cmd+Ctrl+Q) whenever leaving their desk or workstation unattended.
- Printed documents containing confidential, proprietary, or client-identifiable data must be stored in locked filing cabinets when unattended and shredded using cross-cut shredders.

## 4. Remote Work and Network Access
- Remote connections to internal company resources must route through the enterprise GlobalProtect VPN with split-tunneling disabled for corporate subnets.
- Public Wi-Fi networks (e.g., airports, cafes, hotels) must never be used without an active VPN tunnel.
- Personally Owned Devices (BYOD) may only access email, calendar, and approved web applications through Mobile Device Management (MDM) enrolled profiles with remote wipe capabilities. Direct download of proprietary code repositories or client data to personal devices is prohibited.

## 5. Data Classification and Handling
Data assets are categorized into four distinct classification levels:
1. **Public**: Information approved for external public dissemination (e.g., marketing brochures, press releases).
2. **Internal**: Operational documentation, internal wiki articles, and company-wide announcements intended solely for workforce members.
3. **Confidential**: Business plans, financial statements, non-public employee records, and non-sensitive customer operational data. Access is role-restricted.
4. **Restricted**: Highly sensitive client financial records, personally identifiable information (PII), credit card data (PCI-DSS), cryptographic keys, and proprietary source code algorithms. Requires documented manager approval, encryption at rest (AES-256), and encryption in transit (TLS 1.3).

## 6. Removable Media and Storage
- USB flash drives and external hard drives are disabled by endpoint management policy by default.
- Temporary USB read/write exceptions must be requested through IT Service Desk with business justification and manager sign-off.
- Approved cloud storage services are limited to enterprise Microsoft OneDrive and Google Drive instances. Personal storage services (Dropbox, Box, iCloud, WeTransfer) are blocked at the perimeter gateway.

## 7. Incident Response and Reporting
- Any suspected security incident—including phishing emails, ransomware alerts, lost hardware devices, or unauthorized disclosure—must be reported immediately to the Security Operations Center (SOC) at `soc@company.com` or extension 4444 within 1 hour of discovery.
- Employees must not attempt to investigate, shut down, or clean infected systems independently; the system must be isolated from Wi-Fi and ethernet immediately.

## 8. Non-Compliance Penalties
Violations of this security policy may result in immediate suspension of network credentials, formal disciplinary action up to termination of employment, and potential civil or criminal liability where client confidentiality agreements or statutory laws are breached.
