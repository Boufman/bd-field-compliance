# backend/cpvault_seed.py

from backend import cpvault

def seed_cpvault():
    data = cpvault.load_cpvault()

    data["pharmacy_details"] = {
        "name": "Example Community Pharmacy",
        "address": "123 Main Street, Perth WA 6000"
    }

    # Optional but recommended
    data["fridge_id"] = "Vaccine Fridge 1"
    data["active_staff"] = "Pharmacist 1"

    cpvault.save_cpvault(data)
    print("✅ CPVault seeded")

if __name__ == "__main__":
    seed_cpvault()