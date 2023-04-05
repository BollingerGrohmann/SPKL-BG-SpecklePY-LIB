# bg-specklepy
Bollinger+Grohmann Library for SpecklePy.

## Description
Python library aimed at:
* Condensing the coding efforts required in the communication with the speckle server.
* Perform simple operations on a commited model. Example being the column eccentricities check of a Revit model (refer to Examples below)

## Dependencies
Required dependencies are automatically checked. Should a library not be available for a specific class / method, the user will be prompted to install with a simple "y" input on the console. 
* specklepy
* pandas
* numpy
* trimesh

## Examples

### Column eccentricity example
#### Description
Column eccentricities present an undesired disturbance in the flow of forces. In large models, detecting such eccentricities can prove to be a manual and tedious task. In this development, models are interpreted and a graphical output highlights areas where eccentricities are present.
#### Detailed steps
##### 01 Getting started
(hier: Schritte fürs klonen usw.)
##### 02 Revit model
(hier: einfaches Revit model zeigen (mit Stützenversätzen), verlinken usw.)
##### 03 Commit to Speckle server
(hier: wie das mit dem Connector geht. Commit zeigen, server_url, token usw.)
##### 04 Running analysis with columnOffsetEvaluation
(hier: wie einfach das mit dem Code ist)
#### Results
(hier: Einfärbung nach Distanz usw.)

## Contributions
Any and all contributions and collaborations are welcome! 

Please note that this library development is in early stages and a high degree of refinement in code, although wanted, is not priority in these stages of development. Through application on use cases, can the library be refined and further developed to a desired level of quality.
