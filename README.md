# NagiosScroller
Made with 8 Led displays (8X8) driven with Max 7219) wired to a wifi processor NodeMCU 
(ESP8266 Processor), this tool parses the return of a CGI script who list Nagios Alerts.

When there's no alerts, a scrolling dot is displayed every 5s.

Alert is composed of server name, service name and service status. 

Multiples alerts can be aggregated.

1/ Wire your ESP + eight 8X8 Led matrix led display
2/ Install Arduino 1.6+ and ESP8266 adruino addon (see https://learn.sparkfun.com/tutorials/esp8266-thing-hookup-guide/installing-the-esp8266-arduino-addon )
3/ Get NagiosScroller.ino
4/ Adapt it for wfi credentials, 
	const char* ssid     = "SSID";
	const char* password = "PASSWPRD";
5/ Adapt if for your text.cgi location
	const char* url  = "/nagios/cgi-bin/text.cgi";
	const char* host = "www.Myserver.org";
5/ Upload text.cgi to the required location (normally, the same as nagios.cgi)
6/ Test it and enjoy :)