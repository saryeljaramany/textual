import asyncio

from textual.app import App
from textual.widgets._toast import ToastHolder, ToastRack


class NotificationApp(App[None]):
    pass


async def test_app_no_notifications() -> None:
    """An app with no notifications should have an empty notification list."""
    async with NotificationApp().run_test() as pilot:
        assert len(pilot.app._notifications) == 0


async def test_app_with_notifications() -> None:
    """An app with notifications should have notifications in the list."""
    async with NotificationApp().run_test() as pilot:
        pilot.app.notify("test")
        await pilot.pause()
        assert len(pilot.app._notifications) == 1


async def test_app_with_removing_notifications() -> None:
    """An app with notifications should have notifications in the list, which can be removed."""
    async with NotificationApp().run_test() as pilot:
        pilot.app.notify("test")
        await pilot.pause()
        assert len(pilot.app._notifications) == 1
        pilot.app._unnotify(list(pilot.app._notifications)[0])
        assert len(pilot.app._notifications) == 0


async def test_app_with_notifications_that_expire() -> None:
    """Notifications should expire from an app."""
    async with NotificationApp().run_test() as pilot:
        for n in range(10):
            pilot.app.notify("test", timeout=(0.01 if bool(n % 2) else 60))

        # Wait until the 0.01 timeout expires on all notifications (plus some leeway)
        await asyncio.sleep(0.25)
        assert len(pilot.app._notifications) == 5


async def test_app_clearing_notifications() -> None:
    """The application should be able to clear all notifications."""
    async with NotificationApp().run_test() as pilot:
        for _ in range(100):
            pilot.app.notify("test", timeout=120)
        await pilot.pause()
        assert len(pilot.app._notifications) == 100
        pilot.app.clear_notifications()
        assert len(pilot.app._notifications) == 0


async def test_app_clearing_notifications_removes_toast_holders() -> None:
    """Clearing notifications should remove all ToastHolders from the ToastRack (regression test for #6788)."""
    async with NotificationApp().run_test(notifications=True) as pilot:
        for n in range(5):
            pilot.app.notify(f"msg {n}", timeout=60)
        await pilot.pause()
        rack = pilot.app.screen.query_one(ToastRack)
        assert len(rack.query(ToastHolder)) == 5
        pilot.app.clear_notifications()
        await pilot.pause()
        assert len(rack.query(ToastHolder)) == 0
