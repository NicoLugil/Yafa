<head>
<link rel="stylesheet" type="text/css" href="/static/myStyle.css">
<form action="/settings" method="post">
<fieldset>
<legend>Settings</legend>
<p><label for "name">Name</label> <input name="name" type="text" value="{{name}}" style="text-align: right" onfocus="this.select()" onmouseup="return false"/>
<p><label for "temp">Desired Temp</label> <input name="temp" type="text" value="{{temp}}" style="text-align: right" onfocus="this.select()" onmouseup="return false"/>
<p><label for "dHeat_on">Hysteresis Heat ON</label> <input name="dHeat_on" type="text" value="{{dHeat_on}}" style="text-align: right" onfocus="this.select()" onmouseup="return false"/>
<p><label for "dHeat_off">Hysteresis Heat OFF</label> <input name="dHeat_off" type="text" value="{{dHeat_on}}" style="text-align: right" onfocus="this.select()" onmouseup="return false"/>
<p><label for "dCool_on">Hysteresis Cool ON</label> <input name="dCool_on" type="text" value="{{dCool_on}}" style="text-align: right" onfocus="this.select()" onmouseup="return false"/>
<p><label for "dCool_off">Hysteresis Cool OFF</label> <input name="dCool_off" type="text" value="{{dCool_on}}" style="text-align: right" onfocus="this.select()" onmouseup="return false"/>
<p class="submit"><input value="Submit" type="submit" /></p>
<!--
-->
</form>
</fieldset>
<p>Back to <a href="/">root</a></p>
</head>

