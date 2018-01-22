User Verification
=================

Purpose of user verification is to make sure the Meanwise system doesn't have fake users (bots or
trolls). There will be no duplicate accounts allowed (same person having more than 1 account).

To achieve this, we will ask the user to take a video of themselves during registration. In this
video the you will have to say out a sentence that the app give to them randomly from a pre-selected
set of sentences. The sentence is then used as a CAPTHCA to make sure the person who is in the video
is both real and present. The video is then used to do facial recognition of the users face and the
registration is flagged if a duplicate is detected in the system. Manual action will be taken by an
administrative user for duplicate accounts.

Risks

* Live rendering quality and realism.
* Realism of synthetic speech.

Related Posts
=============

Currently related posts is implemented by matching textual descriptions of the posts. But a lot of
the data from the posts are actually the images and/or videos. Therefore we should use object
detection from those images and videos and add those objects that are detected into the post as
extra metadata, which is then used for finding related posts.

This will involve using object detection for find objects in images and sending it to an ML Model to
find what object it is. If an object is not detected then it's passed on to another queue where an
administrative user will manually categorize object which is then used to train the model further.


Augmented Reality
=================

The Augmented Reality feature will allow the user to detect logos, products and other users through
the camera feed. The app will detect the objects in the camera feed and send it to the analysis
engine to detect the object. Information of the detected objects will be sent to the app which then
displays the info next to the object.

Personality Profiling
=====================

We will use 2 sets of data for building a personaly profile for our users. The first data set is the
descriptions from the user's posts. The 2nd data set is the videos of the user from registration and
from interview videos.

Smart Credits
=============

When our users post their work on the app, other users can like those posts. Those likes are counted
as endorsements of the work in the post. For endorsements for their work, the users will get credits
for the skill related to the post. At the beginning 10 endorsements could be 1 credit, but as
credits increase the no. of endorsements needed to get 1 credit increases, eg. 50 endorsements for 1
credit.

The smart credits data will be saved into a Distributed Ledger Technology for auditability and
immutability.
