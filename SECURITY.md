# Threat Model (STRIDE) & Kontrol Keamanan

| STRIDE | Ancaman pada aplikasi | Kontrol / Mitigasi | Diverifikasi oleh |
|--------|-----------------------|--------------------|-------------------|
| **S**poofing | Brute force / login bypass | Password hash (PBKDF2/scrypt), pesan error generik | Pytest, ZAP |
| **T**ampering | SQL Injection pada login/register | Parameterized query, validasi input allow-list | Semgrep, Pytest |
| **R**epudiation | Aksi tidak tercatat | Log request di platform/container | Review |
| **I**nformation Disclosure | Secret bocor di repo, error detail | Secret via env var, Gitleaks, error generik | Gitleaks |
| **D**enial of Service | Library rentan / image rentan | Pin versi dependency, scan CVE | pip-audit, Trivy |
| **E**levation of Privilege | Container berjalan sebagai root | `USER appuser` (non-root) di Dockerfile | Trivy, review |

## Melaporkan Kerentanan
Laporkan secara privat ke ketua tim melalui GitHub Security Advisory pada repo ini.
