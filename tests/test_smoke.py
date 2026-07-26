"""Bootstrap seam: the rivet package must be importable after editable install."""


def test_rivet_package_importable() -> None:
    import rivet

    assert rivet.__version__ == "0.1.0"
