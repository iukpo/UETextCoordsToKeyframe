# UETextCoordsToKeyframe - An Unreal Engine 5.1+ Python script that converts coordinates into positions for animation keyframes

Given a list of coordinates in a text file (and some other inputs), this Unreal Engine Python script converts the coordinates into keyframe positions for a given object and level sequence.

## History

For my Unreal Fellowship, I wanted to be able to animate the path of two meteors in my short film; I wanted the meteors to travel a path in the shape of the infinity symbol, which is better known as a lemniscate. I also wanted to have the meteors move in opposite phase of each other.

The focus of the fellowship was World Building, and I did not have the time to learn how to do animation in Unreal Engine. However, I DO know how to plot a graph from coordinates. I also know Python. So, I wrote two scripts: one to generate the lemniscate path as a series of coordinates written to text file, and another script to convert those coordinates to positions in a keyframe.

In this repo lies my script to convert path coordinates to keyframe positions. As an added bonus, to see how this script works, you get my lemniscate path generation script and a sample UE project to test everything out in!

## How to see this work

You want to see keyframes being generated in the test project? Simply run the `generateKeyFramesFromTextFile.py` script in the test project. This will create the lemniscate paths for the spheres. Then run the level sequence to see the spheres travel along the path!

## How to use this script

The script is located in the `Content\Python` directory of this repo.

You can simply create a folder in your project's `Content\Python` folder and copy the files from this repo in there. Alternatively, you can keep the files in your `Content\Python` folder, but you must add the content of the `__init__.py` to your folder's `__init__.py` to make sure that Unreal will know where to find the functions.

After that, you should be able to make use of the functions after doing `from GenerateKeyFramesFromTextFile.generateKeyFramesFromTextFile import generateLocationKeyFramesFromTextFile` (if you put it into a folder called `GenerateKeyFramesFromTextFile`), or just `from generateKeyFramesFromTextFile import generateLocationKeyFramesFromTextFile` if you do not have the files in a subfolder in `Content\Python`.

Enjoy!


![Shader in Action](Content/Documentation/fellowship_result.png)
