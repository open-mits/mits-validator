from __future__ import annotations

from unittest.mock import patch


def test_main_run() -> None:
    """Test the main run function."""
    from mits_validator.__main__ import run
    
    # Mock uvicorn.run to avoid actually starting the server
    with patch('mits_validator.__main__.uvicorn.run') as mock_run:
        run()
        mock_run.assert_called_once_with(
            "mits_validator.api:app", 
            host="127.0.0.1", 
            port=8000, 
            reload=True
        )

def test_main_entry_point() -> None:
    """Test the main entry point."""
    from mits_validator.__main__ import run
    
    # Mock uvicorn.run to avoid actually starting the server
    with patch('mits_validator.__main__.uvicorn.run') as mock_run:
        # Test that the function can be called
        run()
        assert mock_run.called
