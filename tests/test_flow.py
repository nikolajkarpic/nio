"""The task state machine's refusals (#42 AC-36, AC-56, AC-57). They wait for #45, which builds `nio flow` and the
CLI's state, as the tasks-stage spec's non-goal says. Until then each test says so and passes.
Run: uv run python tests/test_flow.py"""


def waits(test):
    def run():
        print(f"waits for #45 (nio flow): {test.__name__}")
    run.__name__ = test.__name__
    return run


@waits
def test_ac56_the_change_is_refused():
    """T-3 claimed, set to done: refused; it stays claimed and the message names red, green and review."""


@waits
def test_ac57_the_claim_is_refused_and_given_t_5_is_al():
    """T-4 pending on T-1: its claim is refused ("dependencies not done"); a second claim on T-5: "already claimed"."""


@waits
def test_ac36_the_change_is_refused():
    """T-3 green, set to done without a review: refused; it stays green and the message names the missing review."""


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
