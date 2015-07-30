<head>
<link rel="stylesheet" type="text/css" href="/static/myStyle.css">

<h1>Current settings</h1>
<table>
    <tr>
        <td>name</td>
        <td><a href="http://www.homebrew.be/Yafa/{{name}}/">{{name}}</a></td>
    </tr>
    <tr>
        <td>desired temp</td>
        <td>{{temp}}C</td>
    </tr>
    <tr>
        <td>hyst heat On</td>
        <td>{{dHeat_on}}C</td>
    </tr>
    <tr>
        <td>hyst heat Off</td>
        <td>{{dHeat_off}}C</td>
    </tr>
    <tr>
        <td>hyst heat On</td>
        <td>{{dCool_on}}C</td>
    </tr>
    <tr>
        <td>hyst heat Off</td>
        <td>{{dCool_off}}C</td>
    </tr>
</table>

<p><a href="/stop" class="myButton">Stop!</a></p>

<h1>Status</h1>
<h2>Phase</h2>
<table> <tr> <td>
{{mode}} 
</td> </th> </table>
%if mode=='boot':
   <p>booting busy...please refresh in a couple of seconds</p>
%end
%if mode=='wait_for_start':
    <p>Auto-start countdown busy!</p>
    <p>
    <div class="meter">
        <span style="width: {{perc_rem}}%"></span>
    </div>
    </p>
    <h2>New settings</h2>
    <p>Settings can be changed <a href="/settings">here</a>
%end
%if mode=='run':
    <h2>Measured temperature</h2>
    <table> <tr> <td>
    {{temp_meas}}  C
    </td> </th> </table>
    <h2>New settings</h2>
    <p>Settings can be changed <a href="/settings">here</a>
%end
%if mode=='requested2run':
    <p>Will start asap...please <a href="/">refresh</a> in a couple of seconds</p>
<!--






-->
</head>


