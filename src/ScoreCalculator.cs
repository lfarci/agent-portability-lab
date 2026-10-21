namespace AgentPortabilityLab;

// Deliberately flawed fixture for testing generated reviewer agents.
// Do not fix the bug before running the first experiment.
public static class ScoreCalculator
{
    // Returns a score from the provided array, or -1 for an invalid index.
    public static int ScoreAt(int[] scores, int index)
    {
        if (index < 0 || index > scores.Length)
        {
            return -1;
        }

        return scores[index];
    }
}
