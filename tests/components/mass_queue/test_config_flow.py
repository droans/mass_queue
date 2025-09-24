"""Test the config flow."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.mass_queue.config_flow import CONF_URL
from homeassistant.components.mass_queue.const import DEFAULT_TITLE, DOMAIN
from homeassistant.config_entries import SOURCE_IGNORE, SOURCE_USER, SOURCE_ZEROCONF
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from music_assistant_client.exceptions import CannotConnect, InvalidServerVersion
from music_assistant_models.api import ServerInfoMessage

from tests.common import MockConfigEntry


@pytest.fixture
def mock_get_server_info():
    """Mock get_server_info function."""
    with patch(
        "homeassistant.components.mass_queue.config_flow.get_server_info",
        new_callable=AsyncMock,
    ) as mock:
        yield mock


@pytest.fixture
def mock_setup_entry():
    """Mock setup entry."""
    with patch(
        "homeassistant.components.mass_queue.async_setup_entry",
        return_value=True,
    ) as mock:
        yield mock


async def test_user_form(hass: HomeAssistant, mock_get_server_info: AsyncMock) -> None:
    """Test we get the user initiated form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}

    server_info = ServerInfoMessage.from_dict({"server_id": "1234", "base_url": "http://test:8095"})
    mock_get_server_info.return_value = server_info

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_URL: "http://test:8095"},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == DEFAULT_TITLE
    assert result["data"] == {CONF_URL: "http://test:8095"}


async def test_user_form_cannot_connect(
    hass: HomeAssistant, mock_get_server_info: AsyncMock
) -> None:
    """Test we handle cannot connect error."""
    mock_get_server_info.side_effect = CannotConnect

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_URL: "http://test:8095"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_form_invalid_server_version(
    hass: HomeAssistant, mock_get_server_info: AsyncMock
) -> None:
    """Test we handle invalid server version error."""
    mock_get_server_info.side_effect = InvalidServerVersion

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_URL: "http://test:8095"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "invalid_server_version"}


async def test_user_form_unknown_error(
    hass: HomeAssistant, mock_get_server_info: AsyncMock
) -> None:
    """Test we handle unknown error."""
    mock_get_server_info.side_effect = Exception("Unknown error")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_URL: "http://test:8095"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "unknown"}


async def test_user_form_duplicate(
    hass: HomeAssistant, mock_get_server_info: AsyncMock
) -> None:
    """Test we handle duplicate error."""
    mock_config_entry = MockConfigEntry(
        domain=DOMAIN,
        title=DEFAULT_TITLE,
        data={CONF_URL: "http://test:8095"},
        unique_id="1234",
    )
    mock_config_entry.add_to_hass(hass)

    server_info = ServerInfoMessage.from_dict({"server_id": "1234", "base_url": "http://test:8095"})
    mock_get_server_info.return_value = server_info

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_URL: "http://test:8095"},
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_zeroconf_discovery(hass: HomeAssistant, mock_get_server_info: AsyncMock) -> None:
    """Test zeroconf discovery."""
    server_info = ServerInfoMessage.from_dict({"server_id": "1234", "base_url": "http://test:8095"})
    mock_get_server_info.return_value = server_info

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZeroconfServiceInfo(
            host="192.168.1.100",
            port=8095,
            hostname="test.local.",
            type="_music-assistant._tcp.local.",
            name="Music Assistant._music-assistant._tcp.local.",
            properties={"server_id": "1234", "base_url": "http://test:8095"},
        ),
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == DEFAULT_TITLE
    assert result["data"] == {CONF_URL: "http://test:8095"}


async def test_zeroconf_discovery_cannot_connect(
    hass: HomeAssistant, mock_get_server_info: AsyncMock
) -> None:
    """Test zeroconf discovery cannot connect."""
    mock_get_server_info.side_effect = CannotConnect

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZeroconfServiceInfo(
            host="192.168.1.100",
            port=8095,
            hostname="test.local.",
            type="_music-assistant._tcp.local.",
            name="Music Assistant._music-assistant._tcp.local.",
            properties={"server_id": "1234", "base_url": "http://test:8095"},
        ),
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "cannot_connect"


async def test_zeroconf_discovery_missing_server_id(hass: HomeAssistant) -> None:
    """Test zeroconf discovery missing server_id."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZeroconfServiceInfo(
            host="192.168.1.100",
            port=8095,
            hostname="test.local.",
            type="_music-assistant._tcp.local.",
            name="Music Assistant._music-assistant._tcp.local.",
            properties={},  # Missing server_id
        ),
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "missing_server_id"


async def test_zeroconf_existing_entry(
    hass: HomeAssistant, mock_get_server_info: AsyncMock
) -> None:
    """Test zeroconf discovery with existing entry."""
    mock_config_entry = MockConfigEntry(
        domain=DOMAIN,
        title=DEFAULT_TITLE,
        data={CONF_URL: "http://existing:8095"},
        unique_id="1234",
    )
    mock_config_entry.add_to_hass(hass)

    # Mock server info with discovered URL
    server_info = ServerInfoMessage.from_dict({"server_id": "1234", "base_url": "http://discovered:8095"})
    mock_get_server_info.return_value = server_info

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZeroconfServiceInfo(
            host="192.168.1.100",
            port=8095,
            hostname="test.local.",
            type="_music-assistant._tcp.local.",
            name="Music Assistant._music-assistant._tcp.local.",
            properties={"server_id": "1234", "base_url": "http://discovered:8095"},
        ),
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_zeroconf_existing_entry_broken_url(
    hass: HomeAssistant, mock_get_server_info: AsyncMock
) -> None:
    """Test zeroconf discovery with existing entry that has broken URL."""
    mock_config_entry = MockConfigEntry(
        domain=DOMAIN,
        title=DEFAULT_TITLE,
        data={CONF_URL: "http://broken:8095"},
        unique_id="1234",
    )
    mock_config_entry.add_to_hass(hass)

    # Mock server info with discovered URL
    server_info = ServerInfoMessage.from_dict({"server_id": "1234", "base_url": "http://discovered-working-url:8095"})
    mock_get_server_info.return_value = server_info

    # First call fails (broken URL), second call succeeds (discovered URL)
    mock_get_server_info.side_effect = [CannotConnect, server_info]

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZeroconfServiceInfo(
            host="192.168.1.100",
            port=8095,
            hostname="test.local.",
            type="_music-assistant._tcp.local.",
            name="Music Assistant._music-assistant._tcp.local.",
            properties={"server_id": "1234", "base_url": "http://discovered-working-url:8095"},
        ),
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"

    # Verify the URL was updated in the config entry
    updated_entry = hass.config_entries.async_get_entry(mock_config_entry.entry_id)
    assert updated_entry.data[CONF_URL] == "http://discovered-working-url:8095"


async def test_zeroconf_existing_entry_ignored(
    hass: HomeAssistant, mock_get_server_info: AsyncMock
) -> None:
    """Test zeroconf flow when existing entry was ignored."""
    # Create an ignored config entry (no URL field)
    ignored_config_entry = MockConfigEntry(
        domain=DOMAIN,
        title=DEFAULT_TITLE,
        data={},  # No URL field for ignored entries
        unique_id="1234",
        source=SOURCE_IGNORE,
    )
    ignored_config_entry.add_to_hass(hass)

    # Mock server info with discovered URL
    server_info = ServerInfoMessage.from_dict({"server_id": "1234", "base_url": "http://discovered-url:8095"})
    mock_get_server_info.return_value = server_info

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_ZEROCONF},
        data=ZeroconfServiceInfo(
            host="192.168.1.100",
            port=8095,
            hostname="test.local.",
            type="_music-assistant._tcp.local.",
            name="Music Assistant._music-assistant._tcp.local.",
            properties={"server_id": "1234", "base_url": "http://discovered-url:8095"},
        ),
    )
    await hass.async_block_till_done()

    # Should abort because entry was ignored (respect user's choice)
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    # Verify the ignored entry was not modified
    ignored_entry = hass.config_entries.async_get_entry(ignored_config_entry.entry_id)
    assert ignored_entry.data == {}  # Still no URL field
    assert ignored_entry.source == SOURCE_IGNORE
