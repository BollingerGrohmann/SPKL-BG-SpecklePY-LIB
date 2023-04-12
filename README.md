# bg_specklepy
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
Column eccentricities present an undesired disturbance in the flow of forces. In large models, detecting such eccentricities can prove to be a manual and tedious task. In this development, a Revit model is sent to a Speckle branch, interpreted and analysed using the bg_specklepy, with the end result being a graphical output highlighting areas where eccentricities are present.
#### Detailed steps
##### 01 Getting started
In order to use the library, the repository needs to stored locally on your machine. This can be done in one of three ways:
1. Cloning the repository using the *url*;
2. Cloning the repository using GitHub Desktop (**recommended**); and
3. Downloading the files statically as a .zip file (**not recommended**). The static zip file download breaks the link to GitHub, thus further updates will not be automatically "fetched". 
![image](https://user-images.githubusercontent.com/88777268/231439112-e504e818-48ef-4654-8e02-8b68957b9172.png)
Once completed, the repository will appear in the directory of choice:

![image](https://user-images.githubusercontent.com/88777268/231439755-6a6b46bf-0fdc-43bf-bc3a-c29ad7c528b6.png)

If not found, the other libraries used by bg_specklepy (mentioned in "Dependencies") will be automatically installed on your machine following a user prompt.
##### 02 Revit model
A very simple model is shown below. The model contains three sources of column eccentricity / discontinuity which is intentionally modelled in, in order to show the functionality of the script.

![image](https://user-images.githubusercontent.com/88777268/231445510-cb93fc68-a441-4596-9122-cf15d14a16c0.png)

Using the Speckle Connector for Revit, the model can easily be sent to the Speckle server.

![image](https://user-images.githubusercontent.com/88777268/231449020-ff91712d-fccc-4c50-8b61-a2aa429f1d47.png)
##### 03 Speckle server
The model can now be found on the Speckle server.

![image](https://user-images.githubusercontent.com/88777268/231451490-e6e8078f-e037-4a4f-b7e8-e04f60dd5262.png)

For the column offset evaluation to run, two input parameters are required:
- The Speckle server url; and
- The personal access token. (Refer: https://speckle.guide/dev/tokens.html)

##### 04 Running the column eccentricity analysis
Now, the analysis can be run. 
* Navigate to the folder directory *SPKL-BG-SPECKLEPY-LIB > Examples*
* Open the *Analysis_ColumnEccentricity.py* file in your Python environment of choice (for this example, Visual Studio Code was used).

![image](https://user-images.githubusercontent.com/88777268/231452968-c202c361-1738-4cf3-9ac7-9fe4cc8d2418.png)

* The variables "speckle_server" and "speckle_token" require string inputs. Replace the words "insert" with the appropriate parameters.
* The classes Stream, Branch and Commit have an optional field called "index". If the index of the relative items are known in advance, these can be provided as integers. If not, leave the parameters blank and a user prompt will be printed to the console with an appropriate list of options.
* All functions are complete with DocStrings. Should a parameter be unclear, refer to the DocStrings for more information:

![image](https://user-images.githubusercontent.com/88777268/231454300-6b9d3f70-6acf-4cab-b279-7880ee11def3.png)

* For the ```ColumnOffsetEvaluation``` Class, important to note is the ```column_parameter```. This string refers to the Revit Group name for columns and depends on a number of factors such as language in which Revit is being used in. When a false parameter is provided, the user will be prompted with a list of possible names. Update accordingly. For this example, the string "@Tragwerksstützen" will need to be replaced with "@Structural Columns". 

![image](https://user-images.githubusercontent.com/88777268/231455761-eae84dba-5d37-4254-b815-42a7b3c17c61.png)

* When all parameters are correctly provided, the script can be run. Setting ```echo_level``` to 1 keeps users informed of the progress:

![image](https://user-images.githubusercontent.com/88777268/231466068-df92b203-f10d-4349-ae01-7a03ba6687ff.png)

#### Results

The results are automatically commited to a branch called *analysis_column_eccentricity*. If this branch does not exist, it will be created. The offsets are represented by spheres.

![image](https://user-images.githubusercontent.com/88777268/231467560-23d03db1-928c-4d36-b1f5-9c0e41a3111a.png)

By clicking on a sphere object, details to the offset can be interrogated.

![image](https://user-images.githubusercontent.com/88777268/231467830-5df0f7da-804b-4c3a-987e-7048ca2da065.png)

Using the filters, results can be further interpreted. For example, filtering by column discontinuity, we see one sphere returning a 1 (boolean for True) and two spheres returning a 0 (boolean for False). This is as per the defined Revit model. The filters can also be used to colour the spheres according to offset distance (e.g. SRSS which is the square root of the sume of the squares).

![image](https://user-images.githubusercontent.com/88777268/231474246-e6132e51-c368-48bc-aa2d-8cab4183db92.png)

## Contributions
Any and all contributions and collaborations are welcome! 
