#Splits sql from list of strings into parts, so that comments and string literals are isolated and tagged
#End to end goal: determine if the SQL uses a given object yes or no
#            -->  by ignoring the content of string literals and comments, false positives are eliminated
class sqlcodesplitter:
    def __init__(self) -> None:
        self.blanks = [" ", "\t"]
        self.blanks_eoln = [" ", "\t", "\r", "\n"]
        self.bumps = [" ", "\t", "\r", "\n", "--", "'", "/*"]
#
    def FindNonEmpty(self, inlist, from_l, from_c):
        lnr = from_l
        cnr = from_c
        found = False
        while lnr < len(inlist) and found == False:
            while cnr < len(inlist[lnr]) and found == False:
                if inlist[lnr][cnr] in self.blanks_eoln:
                    cnr += 1
                else:
                    found = True
            if found == False:
                cnr = 0
                lnr += 1
        return (lnr, cnr)
#
    def Render(self, inlist, fromto, tag):
        outlist = []
        from_l = fromto[0]
        from_c = fromto[1]
        to_l = fromto[2]
        to_c = fromto[3]
        lnr = from_l
        while lnr < len(inlist) and lnr <= to_l:
            if lnr == from_l:
                c1 = from_c
            else:
                c1 = 0
            if lnr == to_l:
                c2 = to_c
            else:
                c2 = len(inlist[lnr])
            s = inlist[lnr][c1:c2]
            if len(s) > 0:
                outlist.append([s,tag])

            lnr += 1
        return outlist
#
    def FindSingleLineCommentAsNext(self, inlist, from_l, from_c):
        a = self.FindNonEmpty(inlist, from_l, from_c)
        lnr = a[0]
        cnr = a[1]
        lnr_new = -1
        cnr_new = -1
        if lnr < len(inlist):
            if cnr < len(inlist[lnr]) - 1:
                if inlist[lnr][cnr:cnr + 2] == "--":
                    a1 = inlist[lnr][cnr:].find("\n")
                    if a1 == -1:
                        lnr_new = lnr + 1
                        cnr_new = 0
                    else:
                        lnr_new = lnr
                        cnr_new = cnr + a1 + 1
                        if cnr_new > len(inlist[lnr]) - 1:
                            lnr_new = lnr + 1
                            cnr_new = 0
        return (lnr, cnr, lnr_new, cnr_new)
#
    def FindMultiLineCommentAsNext(self, inlist, from_l, from_c):
        a = self.FindNonEmpty(inlist, from_l, from_c)
        lnr = a[0]
        cnr = a[1]
        lnr_new = -1
        cnr_new = -1
        if lnr < len(inlist):
            if cnr < len(inlist[lnr]) - 1:
                if inlist[lnr][cnr:cnr + 2] == "/*":
                    lnr_new = lnr
                    cnr_new = cnr + 2
                    found = False
                    while lnr_new < len(inlist) and found == False:
                        a1 = inlist[lnr_new][cnr_new:].find("*/")
                        if a1 > -1:
                            found = True
                            cnr_new = cnr_new + a1 + 2
                            if cnr_new > len(inlist[lnr_new]) - 1:
                                lnr_new = lnr_new + 1
                                cnr_new = 0
                        else:
                            lnr_new += 1
                            cnr_new = 0

        return (lnr, cnr, lnr_new, cnr_new)
#
    def FindStringLiteralAsNext(self, inlist, from_l, from_c):
        a = self.FindNonEmpty(inlist, from_l, from_c)
        lnr = a[0]
        cnr = a[1]
        lnr_new = -1
        cnr_new = -1

        if lnr < len(inlist):
            if cnr < len(inlist[lnr]):
                if inlist[lnr][cnr] == "'":
                    lnr_new = lnr
                    cnr_new = cnr + 1
                    found = False
                    while lnr_new < len(inlist) and found == False:
                        s_temp = inlist[lnr_new][cnr_new:].replace("''", "@@")
                        a1 = s_temp.find("'")
                        if a1 > -1:
                            found = True
                            cnr_new = cnr_new + a1 + 1
                            if cnr_new > len(inlist[lnr_new]) - 1:
                                lnr_new = lnr_new + 1
                                cnr_new = 0
                        else:
                            lnr_new += 1
                            cnr_new = 0

        return (lnr, cnr, lnr_new, cnr_new)
#
    def FindOthersAsNext(self, inlist, from_l, from_c):
        a = self.FindNonEmpty(inlist, from_l, from_c)
        lnr = a[0]
        cnr = a[1]
        lnr_new = -1
        cnr_new = -1

        if lnr < len(inlist):
            if cnr < len(inlist[lnr]):
                a = -1
                for mychar in self.bumps:
                    a1 = inlist[lnr][cnr:].find(mychar)
                    if a1 > -1 and (a1 < a or a == -1):
                        a = a1
                cnr_new = cnr + a
                lnr_new = lnr
                if a == -1:
                    lnr_new += 1
                    cnr_new = 0
        return (lnr, cnr, lnr_new, cnr_new)
#
    def splitsqlcode(self, inlist):
        outlist = []

        if inlist is None:
            return outlist

        lnr = 0
        cnr = 0
        while lnr < len(inlist) and cnr < len(inlist[lnr]):
            a = self.FindSingleLineCommentAsNext(inlist, lnr, cnr)
            if a[2] > -1 and a[3] > -1:
                o1 = self.Render(inlist,a,"singlelinecomment")
                outlist.extend(o1)
                lnr = a[2]
                cnr = a[3]
            else:
                lnr = a[0]
                cnr = a[1]

            a = self.FindMultiLineCommentAsNext(inlist, lnr, cnr)
            if a[2] > -1 and a[3] > -1:
                o1 = self.Render(inlist,a,"multilinecomment")
                outlist.extend(o1)
                lnr = a[2]
                cnr = a[3]
            else:
                lnr = a[0]
                cnr = a[1]

            a = self.FindStringLiteralAsNext(inlist, lnr, cnr)
            if a[2] > -1 and a[3] > -1:
                o1 = self.Render(inlist,a,"stringliteral")
                outlist.extend(o1)
                lnr = a[2]
                cnr = a[3]
            else:
                lnr = a[0]
                cnr = a[1]

            a = self.FindOthersAsNext(inlist, lnr, cnr)
            if a[2] > -1 and a[3] > -1:
                o1 = self.Render(inlist,a,"other")
                outlist.extend(o1)
                lnr = a[2]
                cnr = a[3]
            else:
                lnr = a[0]
                cnr = a[1]

        return outlist
