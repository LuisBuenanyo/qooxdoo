#!/usr/bin/env python

import sys, string, re, os, random, optparse
import config, tokenizer, filetool


def indentPrint(level, text):
  print "%s%s" % ("  " * level, text)



def getTokenSource(id):
  for key in config.JSTOKENS:
    if config.JSTOKENS[key] == id:
      return key

  return None





def compile(node, level=0, enableNewLines=False, parentType=None):
  indentPrint(level, "%s (%s)" % (node.type, node.get("line", False)))
  compString = ""



  ##################################################################
  # Opening...
  ##################################################################

  if node.type == "map":
    compString += "{"

  elif node.type == "block":
    compString += "{"

  elif node.type == "params":
    compString += "("

  elif node.type == "expression" and parentType == "loop":
    compString += "("

  elif node.type == "loop":
    loopType = node.get("loopType")
    if loopType == "IF":
      compString += "if"
    elif loopType == "WHILE":
      compString += "while"
    else:
      print "UNKNOWN LOOP TYPE: %s" % loopType

  elif node.type == "function":
    functionDeclHasParams = False
    compString += "function"

  elif node.type == "identifier":
    name = node.get("name", False)
    if name != None:
      compString += name

  elif node.type == "call":
    callHasParams = False

  elif node.type == "definition":
    compString += "var %s" % node.get("identifier")

  elif node.type == "constant":
    if node.get("constantType") == "string":
      if node.get("detail") == "singlequotes":
        compString += "'"
      else:
        compString += '"'

      compString += node.get("value")

      if node.get("detail") == "singlequotes":
        compString += "'"
      else:
        compString += '"'

    else:
      compString += node.get("value")

  elif node.type == "keyvalue":
    compString += node.get("key") + ":"

  elif node.type == "return":
    compString += "return "



  ##################################################################
  # Children content
  ##################################################################

  if node.hasChildren():
    childPosition = 1
    childrenNumber = len(node.children)
    previousType = None

    for child in node.children:
      separators = [ "assignment", "call", "definition", "return" ]

      # Separate execution blocks
      if previousType in separators and child.type in separators:
        compString += ";"

        if enableNewLines:
          compString += "\n"



      # Hints for close of node later
      if node.type == "call" and child.type == "params":
        callHasParams = True

      elif node.type == "function":
        if child.type == "params":
          functionDeclHasParams = True

        elif child.type == "body":
          # has no params before body, fix it here, and add body afterwards
          compString += "()"
          functionDeclHasParams = True

      elif node.type == "definition" and child.type == "assignment":
        compString += "="

      elif node.type == "accessor" and child.type == "key":
        compString += "["

      if node.type == "operation" and node.get("left", False) == "true":
        op = node.get("operator")

        if op == "TYPEOF":
          compString += "typeof "
        else:
          compString += getTokenSource(op)



      # Add child
      compString += compile(child, level+1, enableNewLines, node.type)



      if node.type == "operation" and child.type == "first" and node.get("left", False) != "true":
        compString += getTokenSource(node.get("operator"))

      elif node.type == "assignment" and child.type == "left":
        compString += "="

      elif node.type == "accessor" and child.type == "key":
        compString += "]"




      # Separate children in parent list
      if childPosition < childrenNumber:
        if node.type == "variable":
          compString += "."

        elif node.type == "map":
          compString += ","

          if enableNewLines:
            compString += "\n"

        elif node.type == "params":
          compString += ","

          if enableNewLines:
            compString += "\n"





      # Next...
      childPosition += 1
      previousType = child.type





  ##################################################################
  # Closing...
  ##################################################################

  if node.type == "map":
    compString += "}"

  elif node.type == "block":
    compString += "}"

  elif node.type == "params":
    compString += ")"

  elif node.type == "expression" and parentType == "loop":
    compString += ")"

  elif node.type == "call":
    if not callHasParams:
      compString += "()"

  elif node.type == "function":
    if not functionDeclHasParams:
      compString += "()"




  return compString