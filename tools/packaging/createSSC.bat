:: https://stackoverflow.com/questions/84847/how-do-i-create-a-self-signed-certificate-for-code-signing-on-windows
:: Use developer tools command prompt for this

makecert -r -pe -n "CN=wi1k1n SSC" -ss CA -sr CurrentUser -a sha256 -cy authority -sky signature -sv ssc.pvk ssc.cer
pvk2pfx -pvk ssc.pvk -spc ssc.cer -pfx ssc.pfx