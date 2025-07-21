SELO FileFlow Code Signing Guide

To sign the executable with a code signing certificate:

1. Obtain a code signing certificate from a Certificate Authority (CA) like:
   - DigiCert (premium)
   - Sectigo/Comodo (mid-range)
   - GlobalSign (enterprise)
   - GoDaddy (budget-friendly)

2. After obtaining your certificate, use SignTool (part of Windows SDK) to sign the executable:

   signtool.exe sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a "dist\SELO-FileFlow\SELO-FileFlow.exe"

3. To sign the installer after it's created:

   signtool.exe sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a "dist\SELO-FileFlow-Setup-1.0.0.exe"

Note: Without a code signing certificate, Windows may show SmartScreen warnings when users download and run your application.
