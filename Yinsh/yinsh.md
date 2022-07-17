# YINSH : A Competitive Game Environment for COMP90054, Semester 1, 2022
---------------------------------------------------------------------------

### Table of contents

  * [Introduction](#introduction)
     * [Key files to read:](#key-files-to-read)
     * [Other supporting files (do not modify):](#other-supporting-files-do-not-modify)
  * [Rules of YINSH](#rules-of-yinsh)
     * [Layout:](#layout)
     * [Scoring:](#scoring)
     * [Winning:](#winning)
     * [Computation Time:](#computation-time)
  * [Getting Started](#getting-started)
     * [Restrictions:](#restrictions)
     * [Warning:](#warning)
     * [Ranking](#ranking)
  
## Introduction

For COMP90054 this semester, you will be competing against agent teams in YINSH, a strategic board game.
There are many files in this package, most of them implementing the game itself. 

### Key files to read:

* `yinsh_model.py`: The model file that generates game states and valid actions. Start here to understand how everything is structured, and what is passed to your agent. In particular, ```getLegalActions()``` will provide a concise rundown of what a turn consists of, and how that is encapsulated in an action.
* `agents/generic/example_bfs.py`: Example code that defines the skeleton of a basic planning agent. You aren't required to use any of the filled in code, but your agent submitted in `player.py` will at least need to be initialised with __init__(self, _id), and implement SelectAction(self, actions, rootstate) to return a valid action when asked.

### Other supporting files (do not modify):

* `yinsh_runner.py`: Support code to setup and run games. See the loadParameter() function for details on acceptable arguments.
* `yinsh_utils.py`: Stores important constants, such as the integer values used to represent each game piece.

Of course, you are welcome to read and use any and all code supplied. For instance, if your agent is trying to simulate future gamestates, it might want to appropriate code from `yinsh_model.py` in order to do so.


## Rules of YINSH:

### Layout: 

Upon loading YINSH, both Table and Score windows will appear. The Score window will remain in front, tracking each agent's move. At the end of the game, you are able to click on actions in this window and watch the state reload in Table accordingly.

The Table window will display the game board, with each agent's active rings and counters, as well as a set of three ring spaces, to keep score as the game progresses.

### Scoring:

Please read the rules here: https://www.boardspace.net/yinsh/english/rules.htm

We have made a few alterations to these rules for computational reasons:

* If an agent completes multiple sequences (overlapping or crossing), the game will automatically remove the first it sees. The agent is notified of this in the actions provided to it. Since this is a relatively rare occurrence, for the sake of elegance we decided not to ask the agent to make an extra decision here.

* If an agent completes a sequence for its opponent, the game will automatically remove that sequence, along with one of the opponent's rings at random. For the same reason as before, we think it's more streamlined not to have edge cases where agents are being queried multiple times about which counters or rings they want changed. This also opens some interesting strategy; might there be times where finishing an opponent's sequence and forcing them to sacrifice a ring could be beneficial?

### Winning:

The game proceeds turn by turn. If any agent has won three rings (from three sequences made), the game immediately ends, and victory will be theirs. If the game ends with both agents tied for the number of sequences made, they both win. Else, victory goes to the agent with the most sequences when all 51 counters are used.

### Computation Time:

Each agent has 1 second to return each action. Each move which does not return within one second will incur a warning. After three warnings, or any single move taking more than 3 seconds, the game is forfeit. 
There will be an initial start-up allowance of 15 seconds. Your agent will need to keep track of turns if it is to make use of this allowance. 


## Getting Started

**Make sure the version of Python used is >= 3.6, and that you have installed func-timeout (e.g. ```pip install func-timeout```)**

By default, you can run a game against two random agents with the following:

```bash
$ python yinsh_runner.py
```

To change Teal or Magenta agents, use --teal and --magenta respectively, along with the agent path:
```bash
$ python3 yinsh_runner.py --teal agents.MyTeam --magenta agents.anotherTeam
```

If the game renders at a resolution that doesn't fit your screen, try using the argument --half-scale. The game runs in windowed mode by default, but can be toggled to fullscreen with F11.

### Restrictions: 

You are free to use any techniques you want, but will need to respect the provided APIs to have a valid submission. Agents which compute during the opponent's turn will be disqualified. In particular, any form of multi-threading is disallowed, because we have found it very hard to ensure that no computation takes place on the opponent's turn.

### Warning: 

If one of your agents produces any stdout/stderr output during its games in the any tournament (preliminary or final), that output will be included in the contest results posted on the website. Additionally, in some cases a stack trace may be shown among this output in the event that one of your agents throws an exception. You should design your code in such a way that this does not expose any information that you wish to keep confidential.

### Ranking: 

Rankings are determined according to the number of wins/ties in round-robin tournaments, where a win is worth 3 points, a tie is worth 1 point, and losses are worth 0 (Ties are not worth very much to discourage stalemates). Extra credit will be awarded according to the final competition, but participating early in the pre-competitions will increase your learning and feedback. In addition, staff members have entered the tournament with their own devious agents, seeking fame and glory. These agents have team names beginning with `Staff-`.
