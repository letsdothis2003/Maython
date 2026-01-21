By Fahim Tanvir, Labib Nafi, Jude Merryshow, Mooshorof Hossain

Project Name: MAYTHON: Mayo Implementation and showcase in python


---------------------------------------------------------------
Goal and Motivation:
---------------------------------------------------------------
MAYO is a cryptovariete quadratic cryptography scheme which is known for using a really complex system of quadratic formulas and bilinear combination to do its tasks. It is 
knwon for being very fast and adaptable as it addresses a lot of the main issues for mainstream schemes such as RSA while addressing advancements in regular and quantum
computers. 

The team that worked on it did a good job and still is active under NIST standards, so we would like to create a visual simulation of it using their own C implementation. This is done through our 
own implementation with Python which replicates the original C code but relies on Python's really neat libraries. We want to showcase how the scheme operates in thourough detail. 


---------------------------------------------------------------
How our Application works:
---------------------------------------------------------------
MAYO uses quadratic map within a public key, allowing users to sign messages by finding solutions to a system of multivariate equations while making it 
mathematically impossible for attackers to reverse the process without the secret key. These are its parameters:

q (Field Size): The size of the number system. Real MAYO often uses q=16 (numbers from 0 to 15) because it's efficient.
n (Total Variables): The total length of the full signature vector s.
m (Equations): The number of equations in the public key, which matches the size of the hash output (e.g., 64 bytes).
k (Blocks): The number of blocks the signature s is split into (e.g., k=8).
o(Oil Space): The size of a secret part of the key. This is the "trapdoor" that allows Alice to sign, but which Bob (and any attackers) cannot find.


MAYTHON works by converting the algorithm MAYO uses(which you need mayo_alg.py, mayo_utils.py. The file primitives.py 
just ensures the mathematical calculations, which is used in alg.p). Users can test with their own parameters but they are also allowed to use
the NIST presets which are hardcoded in as options. 

mayo.utils and mayo.datasetup are mainly used for initialization as the former helps store constants and utility functions across the entire
project and the latter helps setup the matrices and linear maps which the scheme uses.

we decided to have some fun with this by implementing a password or keyword encryption generation, which takes the set algorithm and creates a encrypted
key using the user's own input(you can also input the seed or randomly generated string as well). You can save it as a txt file just to check it out.


You need mayo_gui.py to run the entire thing as thats what creates the graphical user interface which connected everything together.
We have an .exe file in the "dist" folder of the repository.

In the repository, you can notice that the structure goes from: 
-->main
  --->documentation
  --->implementation

But within our codespace, we created the exe using this format:
-->main
  --->implementation
        --->documentation
(Essentially documentation is within our implementation folder).


---------------------------------------------------------------
Closing thoughts:
---------------------------------------------------------------

This was a fun experience as we got to experience to research and collaborate.
We might make a browser-friendly version using FLASK and any other ways to optimize the code. 

------------------------------------------------------------------------------------------------------------------------------------------------------
