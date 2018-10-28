import numpy as np
from TextRenderer import RenderedTextInformation

def GetRandomText(textInfo, textPool):    
    textPoolLen = len(textPool)
    text = []

    linesLeft = textInfo.maxLines
    while linesLeft > 0:
        glyphsLeft = textInfo.maxGlyphsPerLine
        while glyphsLeft > 0:
            currentChar = textPool[np.random.randint(0, textPoolLen)]
            
            if currentChar == "\n":
                break

            text.append(currentChar)
            glyphsLeft -= 1

        linesLeft -= 1
        text.append("\n")

    return "".join(text)