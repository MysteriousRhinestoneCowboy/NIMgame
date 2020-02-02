from tkinter import *
import random


class Pile:
    def __init__(self, parent, root, signal, width, height, indx=None, color="yellow", wobble=3,
                 coinHeight=None, coinWidth=None, column=None, row=0, maxi=32):
        """Creates a coin pile and assigns it to a list"""
        self.parent = parent
        self.root = root
        self.signal = signal
        self.width = width
        self.height = height
        self.max = maxi
        self.wobble = wobble
        self.bottomBuffer = 3
        self.color = color
        self.play = False

        if indx is None:
            self.indx = self.parent[0]
        else:
            self.indx = indx

        self.resetVal = 0
        self.var = IntVar()

        self.row = row
        if column is None:
            self.column = self.indx
        else:
            self.column = column

        self.row = row
        self.frame = Frame(self.root, width=self.width, height=self.height)
        self.frame.pack_propagate(0)
        self.frame.grid(row=self.row, column=self.column)

        self.button = Button(self.frame, text="reset", command=self.reset)
        self.button.pack(side=BOTTOM, fill=X)

        self.spin = Spinbox(self.frame, textvariable=self.var, to=self.max, from_=0)
        self.spin.pack(side=BOTTOM, fill=X)

        self.canvas = Canvas(self.frame, width=self.width, height=self.height - 65, bg="#F9F9F9")
        self.canvas.pack(side=BOTTOM)

        if coinWidth is None:
            self.coinWidth = 9 * self.width // 10
        else:
            self.coinWidth = coinWidth
        if coinHeight is None:
            self.coinHeight = (self.height - 65) // (self.max + self.bottomBuffer)
        else:
            self.coinHeight = coinHeight
        self.coinStack()
        self.var.set(self.resetVal)
        self.var.trace("w", self.pileChange)

        self.parent.append(self)
        self.parent[0] += 1

    def coinStack(self):
        """Creates the visual representation of the pile"""
        x = (self.width - self.coinWidth) // 2
        y = self.height - 65 - self.bottomBuffer - self.coinHeight

        for i in range(self.max):
            xOffset = random.randint(-1 * self.wobble, self.wobble)
            x0 = x + xOffset
            x1 = x0 + self.coinWidth
            y0 = y - i * self.coinHeight
            y1 = y0 + 2 * self.coinHeight
            self.canvas.create_oval(x0, y0, x1, y1, tags=str(i), fill=self.color, outline="black", state=HIDDEN)

    def restore(self):
        """Restores the pile to its pristine state except for the value of var"""
        self.play = False
        self.resetVal = 0
        self.spin.config(to=self.max)
        self.enable()

    def reset(self):
        """Resets the pile to the saved state"""
        self.var.set(self.resetVal)

    def save(self):
        """Sets the save state to the current pile"""
        self.resetVal = self.get()
        self.spin.config(to=self.get())

    def get(self):
        """Simply returns the size of the pile"""
        return self.var.get()

    def set(self, value):
        """Sets the value of the sandpile"""
        if isinstance(value, int):
            if 0 <= value <= self.max:
                self.var.set(value)

    def randomize(self):
        """Randomly chooses a value for the pile"""
        target = random.randint(1, self.max)
        self.animateSet(target)

    def animateSet(self, target):
        """Sets the value of the sandpile using animateReduction or animateAddition as appropriate"""
        if isinstance(target, int):
            if 0 <= target <= self.max:
                if self.get() > target:
                    self.animateReduction(target)
                elif self.get() < target:
                    self.animateAddition(target)

    def disable(self):
        """Disables the interface of the pile, mostly called from other piles in the parent"""
        self.spin.config(state=DISABLED)
        self.button.config(state=DISABLED)

    def enable(self):
        """Re enables the interface of the pile"""
        self.spin.config(state=NORMAL)
        self.button.config(state=NORMAL)

    def pileChange1(self, a=None, b=None, c=None):
        """Changes the value of the pile and updates the visual"""
        if type(self.get()) == type(0):
            if self.get() <= self.max and self.get() >= 0:
                for i in range(self.max + 1):
                    if i <= self.get():
                        self.canvas.itemconfig(str(i), state=NORMAL)
                    else:
                        self.canvas.itemconfig(str(i), state=HIDDEN)

                if self.play is True:
                    if self.get() != self.resetVal:
                        for pile in self.parent[1:]:
                            if pile is not self:
                                pile.disable()
                    else:
                        for pile in self.parent[1:]:
                            if pile is not self:
                                pile.enable()
            else:
                raise TypeError(f'Value out of range [0, {self.max}]')
        else:
            raise TypeError('Not a valid data type (int)')

    def pileChange(self, a=None, b=None, c=None):
        """Changes the value of the pile and updates the visual"""
        try:
            value = self.get()
        except:
            raise
        else:
            if 0 <= value <= self.max:
                for i in range(self.max + 1):
                    if i <= value:
                        self.canvas.itemconfig(str(i), state=NORMAL)
                    else:
                        self.canvas.itemconfig(str(i), state=HIDDEN)

                if self.play is True:
                    if self.get() != self.resetVal:
                        for pile in self.parent[1:]:
                            if pile is not self:
                                pile.disable()
                    else:
                        for pile in self.parent[1:]:
                            if pile is not self:
                                pile.enable()
            else:
                raise Exception(f'Value out of range [0, {self.max}]')

    def animateReduction(self, target, speed=32):
        """Shows the pile decreasing to the target, one coin/speed (in ms)"""
        if self.get() > target:
            self.var.set(self.get() - 1)
            self.frame.after(speed, lambda x=target: self.animateReduction(x))
        else:
            self.signal.set(self.signal.get() + 1)

    def animateAddition(self, target, speed=32):
        """Shows the pile increasing to the target, one coin/speed (in ms)"""
        if self.get() < target:
            self.var.set(self.get() + 1)
            self.frame.after(speed, lambda x=target: self.animateAddition(x))
        else:
            self.signal.set(self.signal.get() + 1)

    def hide(self):
        """Removes the pile from the GUI but does not destroy the pile. It can still be called and is part of the parent"""
        self.frame.grid_remove()

    def grid(self):
        """Puts the pile back in the GUI if it has been hidden, both functions are currently unused"""
        self.frame.grid()

    def destroy(self, event=None):
        """Removes the pile from the GUI, removes it from the parent, and makes it generally irrelevant"""
        self.frame.destroy()
        self.parent.remove(self)


class NIMgame:
    def __init__(self, maxi=64, piles=3, width=100, height=100):
        self.width = width
        self.menuWidth = 180
        self.height = max(height, 350)
        self.play = False
        self.turn = 0
        self.max = maxi

        self.root = Tk()
        self.root.title("NIM")
        self.piles = [0]
        self.pileFrame = Frame(self.root)
        self.pileFrame.grid(row=1, column=2)
        self.signal = IntVar()
        self.signal.set(0)
        self.signal.trace("w", self.endAI)

        for indx in range(piles):
            Pile(self.piles, self.pileFrame, self.signal, width=self.width, height=self.height, maxi=self.max)

        self.menuFrame = Frame(self.root, width=self.menuWidth, height=self.height)
        self.menuFrame.grid_propagate(0)
        self.menuFrame.grid(row=1, column=1)

        self.statusFrame = Frame(self.menuFrame, width=self.menuWidth, height=60)
        self.statusFrame.grid(row=0)
        self.statusFrame.pack_propagate(0)
        self.gameLabel = Label(self.statusFrame, fg="white")
        self.gameLabel.pack(side=TOP, fill=X)
        self.gameLabel.bind('<Button-2>', self.printNimber)
        self.playerLabel = Label(self.statusFrame, fg="white")
        self.playerLabel.pack(side=TOP, fill=X)

        self.quitFrame = Frame(self.menuFrame, width=self.menuWidth, height=25)
        self.quitFrame.grid(row=1)
        self.quitFrame.pack_propagate(0)
        self.quitButton = Button(self.quitFrame, text="Quit Game", command=self.quitGame)
        self.quitButton.pack(fill=BOTH)

        self.settingFrame = Frame(self.menuFrame, width=self.menuWidth, height=210)
        self.settingFrame.grid(row=2, sticky=E)
        self.settingFrame.pack_propagate(0)
        self.setLabel = Label(self.settingFrame, bg="black", fg="white", text="Settings")
        self.setLabel.pack(side=TOP, fill=X)
        self.optionFrame = Frame(self.settingFrame, width=self.menuWidth - 10, height=185, bg="turquoise")
        self.optionFrame.pack(side=TOP, anchor=E)
        self.optionFrame.pack_propagate(0)
        self.addButton = Button(self.optionFrame, text="Add Pile", command=self.addPile)
        self.addButton.pack(side=TOP, fill=X)
        self.clearButton = Button(self.optionFrame, text="Clear Piles", command=self.clearPiles)
        self.clearButton.pack(side=TOP, fill=X)
        self.randomButton = Button(self.optionFrame, text="Randomize", command=self.randomize)
        self.randomButton.pack(side=TOP, fill=X)
        Frame(self.optionFrame, width=self.menuWidth - 10, height=10).pack(side=TOP)

        self.hotGame = BooleanVar()
        self.hotGame.trace("w", self.updateHotness)
        self.hotGame.set(True)
        self.hotFrame = Frame(self.optionFrame, width=self.menuWidth - 10, height=50)
        self.hotFrame.pack(side=TOP)
        self.hotFrame.pack_propagate(0)
        self.hotButton = Radiobutton(self.hotFrame, text="Hot Game", variable=self.hotGame, value=True,
                                     bg="red", fg="white", indicatoron=0)
        self.hotButton.pack(fill=X)
        self.coldButton = Radiobutton(self.hotFrame, text="Cold Game", variable=self.hotGame, value=False,
                                      bg="blue", fg="white", indicatoron=0)
        self.coldButton.pack(fill=X)
        Frame(self.optionFrame, width=self.menuWidth - 10, height=10).pack(side=TOP)

        self.player1 = IntVar()
        self.player1.trace("w", self.updatePlayers)
        self.player2 = IntVar()
        self.player2.trace("w", self.updatePlayers)
        self.player1.set(0)
        self.player2.set(1)
        self.aiFrame = Frame(self.optionFrame, width=self.menuWidth - 10, height=50)
        self.aiFrame.pack(side=TOP)
        self.aiFrame.pack_propagate(0)
        self.ai1 = Checkbutton(self.aiFrame, text="Player 1 AI", variable=self.player1, indicatoron=0)
        self.ai1.pack(side=TOP, fill=X)
        self.ai2 = Checkbutton(self.aiFrame, text="Player 2 AI", variable=self.player2, indicatoron=0)
        self.ai2.pack(side=TOP, fill=X)
        self.players = [self.player1, self.player2]
        Frame(self.menuFrame, width=self.menuWidth, height=25).grid(row=3)

        self.turnFrame = Frame(self.menuFrame, width=self.menuWidth, height=40)
        self.turnFrame.grid(row=4)
        self.turnFrame.pack_propagate(0)
        self.turnButton = Button(self.turnFrame, text="Start Game", command=self.startGame)
        self.turnButton.pack(fill=BOTH)

        self.root = mainloop()

    def test(self, event=None, gen=100):
        """This is basically just for testing the game, making sure AI works properly, seeing that errors aren't showing up"""
        test = NimTester(self)
        test.generation(gen)

    def addPile(self):
        """Adds a pile to the interface on the right"""
        Pile(self.piles, self.pileFrame, self.signal, width=self.width, height=self.height, maxi=self.max)

    def clearPiles(self):
        """Removes all piles with no coins in them and a reset value of 0"""
        for pile in self.piles[1:]:
            if pile.get() is 0 and pile.resetVal is 0:
                pile.destroy()

    def randomize(self):
        """Randomly assigns a value to each pile"""
        for pile in self.piles[1:]:
            pile.randomize()

    def updateHotness(self, a=None, b=None, c=None):
        """Updates the label in the top left indicating whether the game is hot or cold"""
        if self.hotGame.get() is True:
            self.gameLabel.config(text="Hot Game", bg="red")
        else:
            self.gameLabel.config(text="Cold Game", bg="blue")

    def updatePlayers(self, a=None, b=None, c=None):
        """Updates the label in the top left indicating whose turn it is or who is playing"""
        if self.play is True:
            players = ["Player 1", "Player 2"]
            self.playerLabel.config(text=f'{players[self.turn % 2]}\'s Turn')
        else:
            ai = ["Player", "Computer"]
            self.playerLabel.config(bg="black", fg="white", text=f'{ai[self.player1.get()]} vs {ai[self.player2.get()]}')

    def startGame(self):
        """Starts the game"""
        if self.countPiles() is not 0:
            self.play = True
            self.turn = 0
            self.addButton.config(state=DISABLED)
            self.clearButton.config(state=DISABLED)
            self.randomButton.config(state=DISABLED)
            self.hotButton.config(state=DISABLED)
            self.coldButton.config(state=DISABLED)
            self.ai1.config(state=DISABLED)
            self.ai2.config(state=DISABLED)
            self.quitButton.config(text="End Game", command=self.endGame)
            self.turnButton.config(text="End Turn", command=self.endTurn)
            self.root.title("NIM")
            for pile in self.piles[1:]:
                pile.save()
                pile.play = True
            self.startTurn()
        else:
            raise Exception('There must be at least one pile with one coin to start the game')

    def startTurn(self):
        """Internal function, cannot be directly called by player"""
        self.updatePlayers()
        player = self.players[self.turn % 2].get()
        self.turn += 1
        for pile in self.piles[1:]:
            pile.enable()
        if player == 1:
            self.pileFrame.after(500, self.aiTurn)

    def endTurn(self):
        """Indicates that the player has finished their turn"""
        if self.countPiles() is 0:
            self.endGame()
        else:
            validTurn = False
            for pile in self.piles[1:]:
                if pile.get() != pile.resetVal:
                    pile.save()
                    validTurn = True
            if validTurn is True:
                self.startTurn()
            else:
                raise Exception("At least one pile must be changed")

    def endGame(self):
        """Indicates that the game is over, either because the player has quit or because a player has won"""
        winner = self.getWinner()
        if winner is not None:
            self.root.title(f'{winner} Won the Game')
        self.play = False
        self.addButton.config(state=NORMAL)
        self.clearButton.config(state=NORMAL)
        self.randomButton.config(state=NORMAL)
        self.hotButton.config(state=NORMAL)
        self.coldButton.config(state=NORMAL)
        self.ai1.config(state=NORMAL)
        self.ai2.config(state=NORMAL)
        self.quitButton.config(text="Quit Game", command=self.quitGame)
        self.turnButton.config(text="Start Game", command=self.startGame)
        for pile in self.piles[1:]:
            pile.restore()

    def getWinner(self):
        """Returns the winner of the game, if the game was exited early a result of None is returned"""
        if self.countPiles() is not 0:
            winner = None
        else:
            players = ["Player 1", "Player 2"]
            if self.hotGame.get() is True:
                winner = players[(self.turn + 1) % 2]
            else:
                winner = players[self.turn % 2]
        return winner

    def aiTurn(self):
        """AI takes a turn"""
        move = self.strategize()
        move[0].animateReduction(move[1])

    def endAI(self, a=None, b=None, c=None):
        """AI ends its turn, this was made separate to facilitate timing"""
        if self.play is True:
            self.endTurn()

    def strategize(self):
        """Figures out which strategy to use and returns the optimal move"""
        if self.hotGame.get() is True:
            move = self.hotStrats()
        else:
            move = self.coldStrats()
        return move

    def hotStrats(self):
        """Returns a move that produces a nimber of 0, if that is impossible a random move in returned"""
        nimber = self.nimber()
        if nimber is 0:
            nonEmpty = []
            for pile in self.piles[1:]:
                if pile.get() is not 0:
                    nonEmpty.append(pile)
            move0 = random.choice(nonEmpty)
            move1 = random.randint(0, move0.get() - 1)
        else:
            for pile in self.piles[1:]:
                if pile.get() > pile.get() ^ nimber:
                    move0 = pile
                    move1 = pile.get() ^ nimber
                    break
        return move0, move1

    def coldStrats(self):
        """Usually functions like hotStrats, but once there is exactly one big pile it makes a special move"""
        bigPile = self.countBigPiles()
        if bigPile[1] == 1:
            print("This is my time to shine!")
            move = (bigPile[0], self.countPiles() % 2)
        else:
            move = self.hotStrats()
        return move

    def printNimber(self, event=None):
        """Secret cheaty function that can be called by right-clicking the gameLabel on the top left"""
        print(self.nimber())

    def countBigPiles(self):
        """Counts the number of piles with at least two coins and returns one of those big piles"""
        count = 0
        bigPile = None
        for pile in self.piles[1:]:
            if pile.get() > 1:
                count += 1
                bigPile = pile
        return bigPile, count

    def countPiles(self):
        """Returns the number of piles that are not empty, called by coldStrats"""
        count = 0
        for pile in self.piles[1:]:
            if pile.get() is not 0:
                count += 1
        return count

    def nimber(self):
        """Returns the nimber of all the piles AKA the binomial XOR operator, foundational to all AI functions"""
        nimber = 0
        for pile in self.piles[1:]:
            nimber ^= pile.get()
        return nimber

    def quitGame(self):
        """Ends the game, stops the program"""
        self.root.destroy()


class NimTester:
    def __init__(self, game):
        self.game = game
        self.game.player1.set(1)
        self.game.player2.set(1)
        self.count = 0
        self.victoryLog = []

    def generation(self, generations):
        while self.count < generations:
            self.prepare()
        self.publish()

    def prepare(self):
        for pile in self.game.piles[1:]:
            pile.set(random.randint(0, pile.max))
            pile.save()
            self.game.turn = 0
        self.game.play = True
        if self.game.nimber() == 0:
            prediction = "Player 2"
        else:
            prediction = "Player 1"

        winner = self.playGame()
        self.victoryLog.append((prediction, winner, self.game.turn))

    def playGame(self):
        if self.game.hotGame.get() is True:
            while self.game.countPiles() != 0:
                self.hotTurn()
        else:
            while self.game.countPiles() != 0:
                self.coldTurn()

        winner = self.game.getWinner()
        self.count += 1
        return winner

    def hotTurn(self):
        move = self.game.hotStrats()
        move[0].set(move[1])
        self.game.turn += 1

    def coldTurn(self):
        bigPile = self.game.countBigPiles()
        if bigPile[1] == 1:
            bigPile[0].set(self.game.countPiles() % 2)
            self.game.turn += 1
        else:
            self.hotTurn()

    def publish(self):
        anomalies = [victory for victory in self.victoryLog if victory[0] != victory[1]]
        print(len(anomalies))
        print(anomalies)


game = NIMgame()