import random

from data_generator.generate import N_LOANS, SEED, generate


def dataset():
    return generate(random.Random(SEED))


def test_deterministic_with_seed():
    assert dataset() == dataset()


def test_loan_shape():
    loans, _ = dataset()
    assert len(loans) == N_LOANS
    ids = [loan[0] for loan in loans]
    assert len(set(ids)) == len(ids)


def test_repayments_reference_known_loans():
    loans, repayments = dataset()
    known = {loan[0] for loan in loans}
    assert all(payment[1] in known for payment in repayments)


def test_defaulted_loans_exist():
    loans, repayments = dataset()
    paid_by_loan: dict[str, float] = {}
    for payment in repayments:
        paid_by_loan[payment[1]] = paid_by_loan.get(payment[1], 0) + payment[3]
    unpaid_or_partial = [
        loan for loan in loans
        if paid_by_loan.get(loan[0], 0) < loan[4]  # paid < principal (local ccy)
    ]
    share = len(unpaid_or_partial) / len(loans)
    assert 0.05 < share, "portfolio must contain delinquent loans"


def test_all_amounts_positive():
    loans, repayments = dataset()
    assert all(loan[4] > 0 for loan in loans)
    assert all(payment[3] > 0 for payment in repayments)
