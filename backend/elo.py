# define Elo class for calculating Elo ratings

def expected_score(rating_a, rating_b):
    """Calculate expected score for player A against player B."""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_rating(rating_a, rating_b, score_a):
    """
    Update the Elo rating for player A based on the score against player B.
    
    :param rating_a: Current Elo rating of player A
    :param rating_b: Current Elo rating of player B
    :param score_a: Actual score of player A (1 for win, 0.5 for draw, 0 for loss)
    """
    k = 32  # K-factor, determines the maximum possible adjustment per game
    expected_a = expected_score(rating_a, rating_b)
    return rating_a + k * (score_a - expected_a)
