# PreviewMix
Ver. 0.10<br/>
Requires Python 3.4+

A script for making the previews of musical albums or any tracklists.
The script is basically an ffmpeg wrapper.
 
Note: ffmpeg executable should be located in the script folder
 	    or included in the system path.
 
## Parameters:
--source (-s)

		The source folder containing album tracks
		(required)
		
--destination (-d)

		The destination mp3 file that will contain preview mix
		(by default: '100-preview.mp3' in the source folder)
		
--count (-c)

		The number of tracks to include into preview mix
		(by default: all tracks in the source folder)
		
--framesize (-f)

		The size of a segment to crop from each track
		(by default: 25 seconds)
		
--log (-l)

		Show progress
		(by default: False)

## Usage example:
	previewmix --source "C:\Music\2000 - Album" --count 5 --frame 15 -l

## TODO:
- [x] Create a script with basic functionality
- [ ] Implement intelligent cropping and merging based on various descriptors
- [ ] Evaluate the coefficient of album's musical diversity