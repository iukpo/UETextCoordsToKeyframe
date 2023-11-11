'''
TODOS:
1) Finish cleaning this up. Update calls too to get rid of deprecation. Explain input and output formats.
2) Make filenames consistent according to best practices.
3) Create test world and level sequence for user.
4) Start writing how to use (start from example in main, explain that code is all in GenerateKeyFramesFromTextFile folder, and should just be able to drop into Content/Python of project for use)
5) Test that all works in 5.1.1.
6) Post on GitHub.
'''


import unreal
from enum import Enum
import numpy as np

class AxisOrder(int, Enum):
    X = 0
    Y = 1
    Z = 2

def getActorCoordinateFromTimelineKeyframe(levelseqpath, spawnableActorName, keyframeIdx = 0):
    """
    Get coordinate of actor at keyframe index in timeline.
    levelseqpath = level sequence file path (Ex.: /Game/Maps/LevelSequences/Anim)
    spawnableActorName = name of actor in level sequence
    keyframeIdx = keyframe #
    Note: Level sequence must have at least one keyframe. Otherwise, will error (no transform track).
    """
    frameVals = [0.0,0.0,0.0]

    try:
        levelSeq = unreal.find_asset(levelseqpath)

        if levelSeq:

            unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(levelSeq)

            # Get bindings from spawnable actor in level sequence (presumes actor is already a spawnable)
            spawnables = levelSeq.get_spawnables()
            actorspawnable = None
            for spawnable in spawnables:
                #print("Spawnable name: {0}".format(spawnable.get_display_name()))
                if (spawnable.get_display_name() == spawnableActorName):
                    #print("Spawnable found!")
                    actorspawnable = spawnable
                    break
            transformtracks = unreal.MovieSceneBindingExtensions.find_tracks_by_exact_type(actorspawnable,
                                                                                           unreal.MovieScene3DTransformTrack)
            if transformtracks:
                # Track containing transforms - presumed to be the only one returned in an array for transforms.
                maintransformtrack = transformtracks[0]

                # print("Number of items in transform track array: {0}".format(str(len(transformtracks))))

                # Get sections within track (sections are location, rotation, scale).
                transformsections = maintransformtrack.get_sections()

                # Get location section
                locationsection = transformsections[0]

                # Get section channels
                sectionchannels = locationsection.get_all_channels()

                #Store points in array
                frameVals[0] = sectionchannels[0].get_keys()[keyframeIdx].get_value()
                frameVals[1] = sectionchannels[1].get_keys()[keyframeIdx].get_value()
                frameVals[2] = sectionchannels[2].get_keys()[keyframeIdx].get_value()
    except Exception as err:
        print("Error in getActorCoordinateFromTimelineKeyframe: "+str(err))

    return frameVals

def generateLocationKeyFramesFromTextFile(levelseqpath, spawnableActorName, inputPointsFile, axisorder = [AxisOrder.Y,AxisOrder.Z,AxisOrder.X], startingkeyframe = 0, keyframeFreq=30):
    """
    Creates keyframes from input text file.
    Text file should just have a series of 3D coordinates per line, with each line representing a keyframe.
    Axis order determines component of each coordinate (Ex.: (1,2,3) may be points in (Z,Y,X) order).
    levelseqpath = level sequence file path (Ex.: /Game/Maps/LevelSequences/Anim)
    spawnableActorName = name of actor in level sequence. Needs to be a spawnable for this release.
    inputPointsFile = path to file containing points
    startingkeyframe = starting key frame (does not necessarily have to be zero!)
    keyframeFreq = Keyframe frequency (keyframe ever fifteen frames, etc.)
    Note: Level sequence must have at least one keyframe. Otherwise, will error (no transform track).
    """
    levelSeq = unreal.find_asset(levelseqpath)
    if levelSeq:

        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(levelSeq)

        # Get bindings from spawnable actor in level sequence (presumes actor is already a spawnable)
        spawnables = levelSeq.get_spawnables()
        actorspawnable = None
        for spawnable in spawnables:
            # print("Spawnable name: {0}".format(spawnable.get_display_name()))
            if (spawnable.get_display_name() == spawnableActorName):
                # print("Spawnable found!")
                actorspawnable = spawnable
                break
        transformtracks = unreal.MovieSceneBindingExtensions.find_tracks_by_exact_type(actorspawnable,
                                                                                       unreal.MovieScene3DTransformTrack)

        print(transformtracks)

        #Track containing transforms presumed to be only one returned in an array for transforms.
        maintransformtrack = transformtracks[0]

        #print("Number of items in transform track array: {0}".format(str(len(transformtracks))))

        #Get sections within track (sections are location, rotation, scale).
        transformsections = maintransformtrack.get_sections()

        #Get location section
        locationsection = transformsections[0]

        # Get section channels.
        locationsectionchannels = locationsection.get_all_channels()

        # Remove all existing keys in each channel of the location section to make a clean slate.
        for channel in locationsectionchannels:
            channelkeys = channel.get_keys()
            for key in channelkeys:
                channel.remove_key(key)

        # Initialise keyframe index to starting key frame.
        keyframeIdx = startingkeyframe

        # Variables for each coordinate read in from file.
        x = 0
        y = 0
        z = 0

        #Add in the points, but in the order of axis order so that change only occurs on desired axes.
        with open(inputPointsFile, 'r') as file:
            for line in file:
                x, y, z = line.split(",")
                locationsectionchannels[0].add_key(time=unreal.FrameNumber(int(keyframeIdx)), new_value=float(x))
                locationsectionchannels[1].add_key(time=unreal.FrameNumber(int(keyframeIdx)),
                                                      new_value=float(y))
                locationsectionchannels[2].add_key(time=unreal.FrameNumber(int(keyframeIdx)),
                                                      new_value=float(z))
                keyframeIdx = keyframeIdx + keyframeFreq

        # Refresh to visually see the new binding added
        unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
    else:
        print("Level sequence {0} not found!".format(levelseqpath))

if __name__ == "__main__":
    """
    Code to test GenerateKeyFramesFromTextFile. Uses generateLemniscatePathPoints to move two sample objects
    in a path the shape of the infinity symbol (lemniscate). One object will travel "clockwise", the other
    will travel in the opposite direction.
    """
    import os

    import numpy as np

    def generateLemniscatePathPoints(printPlot=False, outputFileName='lemniscate.txt', numPoints=100, alpha=1,
                                     oppositePhase=False, xDisp=0, yDisp=0, zDisp=0):
        """
        Function used to generate a path in the shape of a lemniscate (infinity symbol).
        This function is provided as an example function to use for generating points to plot with GenerateKeyFramesFromText File;
        I wrote it for my Unreal Fellowship project.
        It has been adapted from https://stackoverflow.com/questions/27795765/pyplot-lemniscate
        printPlot = flag determining whether or not to print a visual plot of the path after writing file to path.
        outputFileName = Output file name
        numPoints = num points in the path
        alpha = Amplitude of the lemniscate loop. As this number increases, so does the size of the loop.
        oppositePhase = Not so much opposite direction, but a path where the the lemniscate is drawn in opposite phase to default implementation.
        xDisp, yDisp, zDisp = displacement between points
        """
        t = np.linspace(0, 2 * np.pi, num=numPoints)

        x = [(alpha * np.sqrt(2) * np.cos(i) / (np.sin(i) ** 2 + 1)) + xDisp for i in t]

        y = [(alpha * np.sqrt(2) * np.cos(i) * np.sin(i) / (np.sin(i) ** 2 + 1)) + yDisp for i in t]

        # Assume a constant z of zero (if there is a formula for z component, use here).
        z = 0.0 + zDisp

        # Save the points to a file that will be read in by Unreal.
        updatedNumberOfPoints = len(x)
        if (not printPlot):
            if (oppositePhase):
                x.reverse()
                y.reverse()

            with open(outputFileName, 'w') as file:
                # print("updatedNumberOfPoints: {0}".format(str(updatedNumberOfPoints)))
                for i in range(0, updatedNumberOfPoints - 1):
                    file.write(
                        "{0},{1},{2}\n".format(x[i], y[i], z))

        else:
            import matplotlib.pyplot as plt
            plt.plot(x, y)
            plt.show()

    def generateLemniscatePoints(levelseqpath, spawnableActorName, outputPointsFile, size = 1000, revDirection=False):
        initialActorLocation=getActorCoordinateFromTimelineKeyframe(levelseqpath, spawnableActorName)
        generateLemniscatePathPoints(printPlot=False, outputFileName=outputPointsFile, numPoints=100, alpha=size,
                           oppositePhase=revDirection, xDisp=initialActorLocation[0], yDisp=initialActorLocation[1], zDisp=initialActorLocation[2])
    
    workingDirectory = os.path.dirname(os.path.abspath(__file__)) + "\\"
    lemniscatePointsFile = workingDirectory+'clockwise.txt'
    reverseLemniscatePointsFile = workingDirectory + 'counterclockwise.txt'
    levelseqpath = "/Game/AnimationSequence"
    spawnableActorName = "ClockwiseSphere"
    otherSpawnableActorName = "CounterClockwiseSphere"
    
    #Generate the lemniscate path points
    pathSizeMag = 1000
    generateLemniscatePoints(levelseqpath, spawnableActorName, lemniscatePointsFile, size=pathSizeMag)
    generateLemniscatePoints(levelseqpath, otherSpawnableActorName, reverseLemniscatePointsFile, size=pathSizeMag, revDirection=True)

    #Generate plot points according to current location of actor.
    generateLocationKeyFramesFromTextFile(levelseqpath,spawnableActorName,lemniscatePointsFile, keyframeFreq= 1)
    generateLocationKeyFramesFromTextFile(levelseqpath, otherSpawnableActorName,reverseLemniscatePointsFile, keyframeFreq= 1)