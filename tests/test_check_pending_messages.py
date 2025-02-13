import pytest
import json
import asyncio
from pathlib import Path
import tempfile
import shutil
from datetime import datetime, timezone
from activities.activity_check_pending_messages import CheckPendingMessagesActivity
from framework.main import DigitalBeing
from framework.memory import Memory
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def temp_storage():
    """Create a temporary storage directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_memory_with_pending(temp_storage):
    """Create a mock memory file with pending messages."""
    storage_path = Path(temp_storage)
    memory_file = storage_path / "memory.json"
    
    # Create test memory data
    memory_data = {
        "short_term": [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "activity_type": "UserChatMessage",
                "success": True,
                "error": None,
                "data": {"status": "pending", "message": "Hello?"},
                "metadata": {}
            },
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "activity_type": "OtherActivity",
                "success": True,
                "error": None,
                "data": {},
                "metadata": {}
            }
        ],
        "long_term": {}
    }
    
    # Write mock memory file
    memory_file.parent.mkdir(exist_ok=True)
    with open(memory_file, 'w') as f:
        json.dump(memory_data, f)
    
    print(f"\nCreated mock memory file at: {memory_file}")
    print(f"File contents: {memory_file.read_text()}")  # Verify file contents
    
    return temp_storage

@pytest.fixture
def mock_memory_without_pending(temp_storage):
    """Create a mock memory file without pending messages."""
    storage_path = Path(temp_storage)
    memory_file = storage_path / "memory.json"
    
    memory_data = {
        "short_term": [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "activity_type": "UserChatMessage",
                "success": True,
                "error": None,
                "data": {"status": "completed", "message": "Hello!"},
                "metadata": {}
            }
        ],
        "long_term": {}
    }
    
    memory_file.parent.mkdir(exist_ok=True)
    with open(memory_file, 'w') as f:
        json.dump(memory_data, f)
    
    return temp_storage

@pytest.mark.asyncio
async def test_pending_messages_found(mock_memory_with_pending, monkeypatch):
    """Test that the activity correctly identifies pending messages."""
    print("\nStarting test_pending_messages_found")
    
    # Mock DigitalBeing to use our test storage
    def mock_initialize(self):
        self.storage_path = mock_memory_with_pending
        self.memory = Memory(storage_path=mock_memory_with_pending)  # Create new Memory with correct path
    
    monkeypatch.setattr(DigitalBeing, "initialize", mock_initialize)
    
    # Execute activity
    activity = CheckPendingMessagesActivity()
    result = await activity.execute({})
    
    # Add debug logging
    print(f"Activity result: {result.data}")
    print(f"Activity success: {result.success}")
    
    assert result.success is True
    assert result.data["pending_messages"] is True

@pytest.mark.asyncio
async def test_no_pending_messages(mock_memory_without_pending, monkeypatch):
    """Test that the activity correctly handles case with no pending messages."""
    # Mock DigitalBeing to use our test storage
    def mock_initialize(self):
        self.storage_path = mock_memory_without_pending
        self.memory = Memory(storage_path=mock_memory_without_pending)  # Create new Memory with correct path
    
    monkeypatch.setattr(DigitalBeing, "initialize", mock_initialize)
    
    # Execute activity
    activity = CheckPendingMessagesActivity()
    result = await activity.execute({})
    
    assert result.success is True
    assert result.data["pending_messages"] is False

@pytest.mark.asyncio
async def test_empty_memory(temp_storage, monkeypatch):
    """Test handling of empty memory file."""
    # Create empty memory file
    storage_path = Path(temp_storage)
    memory_file = storage_path / "memory.json"
    memory_file.parent.mkdir(exist_ok=True)
    with open(memory_file, 'w') as f:
        json.dump({"short_term": [], "long_term": {}}, f)
    
    def mock_initialize(self):
        self.storage_path = temp_storage
        self.memory = Memory(storage_path=temp_storage)  # Create new Memory with correct path
    
    monkeypatch.setattr(DigitalBeing, "initialize", mock_initialize)
    
    activity = CheckPendingMessagesActivity()
    result = await activity.execute({})
    
    assert result.success is True
    assert result.data["pending_messages"] is False 