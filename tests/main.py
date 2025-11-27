import unittest

from tests.application.converter.commands.convert_images_command_test_case import ConvertImagesCommandTestCase


def main() -> None:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(ConvertImagesCommandTestCase))

    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == "__main__":
    main()
