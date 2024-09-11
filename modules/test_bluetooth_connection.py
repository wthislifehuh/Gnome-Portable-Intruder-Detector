import asyncio
from bleak import BleakClient, BleakScanner

async def find_devices():
    devices = await BleakScanner.discover()
    print("Found devices --------------------------------")
    for device in devices:
        # Handle the case where the device name is None
        device_name = device.name if device.name is not None else "Unknown"
        print(f"Device name: {device_name}, Address: {device.address}")


async def list_services(device_address):
    async with BleakClient(device_address) as client:
        services = await client.get_services()
        for service in services:
            print(f"Service: {service.uuid}")
            for characteristic in service.characteristics:
                print(f"    Characteristic: {characteristic.uuid}")

async def find_and_list_services():
    devices = await BleakScanner.discover()
    found = False
    for device in devices:
        # Ensure the device name is not None before checking
        if device.name and "MI" in device.name:
            print(f"Found device: {device.name} ({device.address})")
            await list_services(device.address)
            found = True
            break
    if not found:
        print("Device not found. Please make sure the device is discoverable.")

# Run the device discovery and service listing
asyncio.run(find_devices())
asyncio.run(find_and_list_services())
