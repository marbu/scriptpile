#!/usr/bin/env runhaskell

--
-- Stupid cat implementation in Haskell.
--

import System.Environment
import System.IO


cat :: Handle -> IO ()
cat h = do
  s <- hGetContents h
  putStr s

filePathCat :: FilePath -> IO ()
filePathCat f = do
  h <- openFile f ReadMode
  cat h
  hClose h

main :: IO ()
main = do
  args <- getArgs
  if length args == 0
    then do cat stdin
    else do mapM_ filePathCat args
