:: https://stackoverflow.com/questions/252226/signing-a-windows-exe-file
:: Use developer tools command prompt for this

signtool sign /a /f ssc.pfx /d SHA256 /tr http://timestamp.digicert.com /td SHA256 ./dist/C4DVersionManager/C4DVersionManager.exe