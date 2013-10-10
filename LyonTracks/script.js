function Evan()
{
document.getElementById("person_name").innerHTML="Evan Chessman";
replaceEntryWithFileContents("./people/Evan_Chessman.txt")
}

function Alicia()
{
document.getElementById("person_name").innerHTML="Alicia Herbert";
replaceEntryWithFileContents("./people/Alicia_Herbert.txt")
}

function Julia()
{
document.getElementById("person_name").innerHTML="Julia Morneau";
replaceEntryWithFileContents("./people/Julia_Morneau.txt")
}

function Richard()
{
document.getElementById("person_name").innerHTML="Richard Neal";
replaceEntryWithFileContents("./people/Richard_Neal.txt")
}

function Development()
{
document.getElementById("person_name").innerHTML="Developement";
replaceEntryWithFileContents("./behind_the_scenes/Development.txt")
}

function Architecture()
{
document.getElementById("person_name").innerHTML="Architecture";
replaceEntryWithFileContents("./behind_the_scenes/Architecture.txt")
}

function Code()
{
document.getElementById("person_name").innerHTML="Our Code";
//document["imgName"].src="./images/xml_code.jpeg/";
//document.write("<img src=\"./images/xml_code.jpeg/\" />");
//alert("JAVASCRIPT");
}


function replaceEntryWithFileContents(fileName) 
{
var xmlhttp;
if (window.XMLHttpRequest)
  {// code for IE7+, Firefox, Chrome, Opera, Safari
  xmlhttp=new XMLHttpRequest();
  }
else
  {// code for IE6, IE5
  xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
xmlhttp.onreadystatechange=function()
  {
  if (xmlhttp.readyState==4 && xmlhttp.status==200)
    {
    document.getElementById("entry").innerHTML=xmlhttp.responseText;
    }
  }

xmlhttp.open("GET",fileName,true);
xmlhttp.send();
}
