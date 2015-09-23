#!/bin/bash

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" > /opt/pyrame/calxml_defaults.xml
echo "<defaultConfig name=\"calxml_defaults\">" >> /opt/pyrame/calxml_defaults.xml
cat /opt/pyrame/calxml_defaults.d/* >> /opt/pyrame/calxml_defaults.xml
echo "</defaultConfig>" >> /opt/pyrame/calxml_defaults.xml

