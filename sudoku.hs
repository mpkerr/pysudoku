import System.Environment
import Data.Array
import qualified Data.Set as S

{- Generate array indices for the cells in a column,
 - a row, or a block -}
col (i,j) = [(p,j) | p <- [0..8]]
row (i,j) = [(i,q) | q <- [0..8]]
block (i,j) = [(p,q) | p <- [m..m+2], q <- [n..n+2]]
    where m = 3 * (div i 3)
          n = 3 * (div j 3)

{- Determine the possible values open to a given cell
 - in a game array -}
values :: (Array (Integer, Integer) Int) -> (Integer, Integer) -> S.Set Int
values g (i,j)
    | g ! (i,j) /= 0 = S.singleton (g ! (i,j))
    | otherwise      = S.difference (S.fromList [0..9]) (S.union bs (S.union rs cs))
    where bs = S.fromList [ g ! c | c <- block (i,j) ]
          rs = S.fromList [ g ! c | c <- row (i,j) ]
          cs = S.fromList [ g ! c | c <- col (i,j) ]

{- Locate open, or unmarked, cells. That is, cells
 - that have not yet been assigned a value -}
unmarked g = filter (\c -> g ! c == 0) (indices g)

{- Test a game array for completeness. A game array is
 - complete when it is completely marked and the
 - marking is valid (all rows contain all 9 digits) -}
complete g = length (unmarked g) == 0 && valid
    where 
        valid = foldl (\x y -> x && (y == S.fromList [1..9])) True 
            [ S.fromList [ g ! c | c <- row (i,0) ] | i <- [0..8] ]

{- Find open cells with n available values -}
tuples n g = map (\x -> (x, S.toList (values g x))) (filter (\c -> S.size (values g c) == n) (unmarked g))
{- Convenience function for locating all cells that
 - have exactly one possible value -}
singles = tuples 1

{- Play a game array. Generate a new game array by setting
 - all cells with only a single possible value, or generate
 - game arrays by selecting each of the available values, in turn,
 - from the first unmarked cell on the board. Carry on recursively
 - until a solution is found or there are no remaining possibilities -}
play :: (Array (Integer, Integer) Int) -> (Array (Integer, Integer) Int)
play g 
    | length (unmarked g) == 0  = g
    | length (singles g) /= 0   = play (g // (map (\x -> (fst x, head (snd x))) (singles g)))
    | length gs /= 0            = head gs
    | otherwise                 = g
    where
        gs = filter complete 
            [play (g // [(x, y)]) | x <- [head (unmarked g)], y <- S.toList (values g x)]

{- String representation of a board -}
dump g = concat [ (unwords $ map show [ g ! (i,j) | j <- [0..8] ]) ++ "\n" | i <- [0..8] ]

{- Command-line driver -}
main :: IO ()
main = do
    args <- getArgs
    game <- readSudoku (args !! 0)
    putStrLn $ dump (play game)

{- Read a simple text format sudoku puzzle -}
readSudoku :: String -> IO (Array (Integer, Integer) Int)
readSudoku fileName = do
    content <- readFile fileName
    let value = read :: String -> Int
    let matrix = map value . concat . map words . lines
    return $ listArray ((0,0),(8,8)) (matrix content)

