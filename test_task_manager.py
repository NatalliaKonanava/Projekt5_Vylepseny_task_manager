import pytest
import mysql.connector
from mysql.connector import Error


# --- Připojení k TESTOVACÍ databázi ---
def pripojeni_test_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="task_manager_test"
        )
        return connection
    except Error as e:
        print(f"Chyba připojení k testovací databázi: {e}")
        return None


# --- Vyčištění tabulky po každém testu ---
@pytest.fixture(autouse=True)
def cleanup():
    connection = pripojeni_test_db()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM ukoly;")
        connection.commit()
        cursor.close()
        connection.close()
    yield
    connection = pripojeni_test_db()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM ukoly;")
        connection.commit()
        cursor.close()
        connection.close()


# ============================
#  TESTY PRO PRIDAT_UKOL()
# ============================

def test_pridat_ukol_pozitivni():
    """Pozitivní test – úkol se správně uloží do DB"""
    connection = pripojeni_test_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO ukoly (nazev, popis, stav)
        VALUES (%s, %s, %s);
    """, ("Testovací úkol", "Toto je testovací popis", "Nezahájeno"))
    connection.commit()

    cursor.execute("SELECT * FROM ukoly WHERE nazev = 'Testovací úkol';")
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    assert result is not None
    print("Pozitivní test přidání úkolu – OK")


def test_pridat_ukol_negativni():
    """Negativní test – pokus o přidání úkolu bez názvu"""
    connection = pripojeni_test_db()
    cursor = connection.cursor()

    # Pokus o vložení prázdného názvu
    cursor.execute("INSERT INTO ukoly (nazev, popis, stav) VALUES (%s, %s, %s);", ("", "Popis", "Nezahájeno"))
    connection.commit()

    # Ověření, že sice proběhlo vložení, ale název je prázdný
    cursor.execute("SELECT * FROM ukoly WHERE nazev = '';")
    result = cursor.fetchall()
    connection.close()

    # Negativní test = nesprávné chování => záznam existuje
    # Ověříme, že je tam 1 úkol s prázdným názvem, což znamená, že
    # aplikace by to měla ošetřit (DB ne).
    assert len(result) == 1

# ============================
#  TESTY PRO AKTUALIZOVAT_UKOL()
# ============================

def test_aktualizovat_ukol_pozitivni():
    """Pozitivní test – úkol se úspěšně aktualizuje"""
    connection = pripojeni_test_db()
    cursor = connection.cursor()

    # Přidáme testovací úkol
    cursor.execute("""
        INSERT INTO ukoly (nazev, popis, stav)
        VALUES (%s, %s, %s);
    """, ("Aktualizace test", "Test popis", "Nezahájeno"))
    connection.commit()

    # Získáme ID
    cursor.execute("SELECT id FROM ukoly WHERE nazev = 'Aktualizace test';")
    id_ukolu = cursor.fetchone()[0]

    # Aktualizujeme stav
    cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s;", ("Hotovo", id_ukolu))
    connection.commit()

    # Ověříme výsledek
    cursor.execute("SELECT stav FROM ukoly WHERE id = %s;", (id_ukolu,))
    stav = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    assert stav == "Hotovo"
    print("Pozitivní test aktualizace úkolu – OK")


def test_aktualizovat_ukol_negativni():
    """Negativní test – pokus o aktualizaci neexistujícího ID"""
    connection = pripojeni_test_db()
    cursor = connection.cursor()

    cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s;", ("Probíhá", 9999))
    connection.commit()

    assert cursor.rowcount == 0  # žádný řádek nebyl změněn

    cursor.close()
    connection.close()
    print("Negativní test aktualizace úkolu – OK")


# ============================
#  TESTY PRO ODSTRANIT_UKOL()
# ============================

def test_odstranit_ukol_pozitivni():
    """Pozitivní test – úkol se úspěšně odstraní"""
    connection = pripojeni_test_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO ukoly (nazev, popis, stav)
        VALUES (%s, %s, %s);
    """, ("Smazat test", "Tento úkol bude smazán", "Nezahájeno"))
    connection.commit()

    # Získáme ID úkolu
    cursor.execute("SELECT id FROM ukoly WHERE nazev = 'Smazat test';")
    id_ukolu = cursor.fetchone()[0]

    # Odstraníme úkol
    cursor.execute("DELETE FROM ukoly WHERE id = %s;", (id_ukolu,))
    connection.commit()

    # Ověříme, že je smazán
    cursor.execute("SELECT * FROM ukoly WHERE id = %s;", (id_ukolu,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    assert result is None
    print("Pozitivní test odstranění úkolu – OK")


def test_odstranit_ukol_negativni():
    """Negativní test – pokus o smazání neexistujícího úkolu"""
    connection = pripojeni_test_db()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM ukoly WHERE id = %s;", (9999,))
    connection.commit()

    assert cursor.rowcount == 0  # žádný úkol nebyl smazán

    cursor.close()
    connection.close()
    print("Negativní test odstranění úkolu – OK")