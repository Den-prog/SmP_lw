<?php

// Task 5 requires a class that creates a transaction in its constructor
class DatabaseSetup {
    private $pdo;

    public function __construct($dsn, $user = null, $password = null) {
        try {
            // Task 1: З'єднання з базою даних за допомогою PDO
            echo "<h3>Завдання 1 & 5: З'єднання та транзакція в конструкторі</h3>";
            $this->pdo = new PDO($dsn, $user, $password);
            $this->pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            
            // Task 5: Транзакція під час створення та заповнення таблиць
            $this->pdo->beginTransaction();
            
            // Створення таблиці
            $this->pdo->exec("CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )");
            
            // Очищення таблиці для чистоти експерименту (щоб при оновленні сторінки не було дублів)
            $this->pdo->exec("DELETE FROM users");

            // Заповнення таблиці
            $this->pdo->exec("INSERT INTO users (name, email) VALUES ('Іван', 'ivan@example.com')");
            $this->pdo->exec("INSERT INTO users (name, email) VALUES ('Марія', 'maria@example.com')");
            
            $this->pdo->commit();
            echo "<p style='color:green;'>Базу даних та таблицю успішно створено та заповнено в межах транзакції.</p>";
            
        } catch (PDOException $e) {
            // Task 4: Відстеження помилок (PDOException, errorCode, errorInfo)
            // Task 5: Повідомлення про неможливість створення БД
            if ($this->pdo && $this->pdo->inTransaction()) {
                $this->pdo->rollBack();
            }
            echo "<p style='color:red;'>Помилка при створенні бази даних або таблиць.</p>";
            echo "<b>Завдання 4:</b> Деталі помилки:<br>";
            echo "Код помилки (errorCode): " . $e->getCode() . "<br>";
            if ($this->pdo) {
                echo "Додаткова інформація (errorInfo): " . print_r($this->pdo->errorInfo(), true) . "<br>";
            }
            echo "Повідомлення: " . $e->getMessage() . "<br>";
        }
    }

    public function getPDO() {
        return $this->pdo;
    }
}

// Instantiate class to run Tasks 1, 5
$dbSetup = new DatabaseSetup('sqlite:lab.db');
$pdo = $dbSetup->getPDO();

if ($pdo) {
    // Task 4: Спробуйте відстежити помилки (Спеціально генеруємо помилку для демонстрації)
    echo "<h3>Завдання 4: Відстеження помилок (PDOException, errorCode, errorInfo)</h3>";
    try {
        // Навмисна синтаксична помилка в SQL-запиті для виклику виключення
        $pdo->query("SELECT * FROM non_existent_table_123");
    } catch (PDOException $e) {
        echo "<div style='background-color:#ffe6e6; border:1px solid red; padding:10px; margin-bottom:15px;'>";
        echo "<p style='color:red;'><b>Спіймано навмисну помилку:</b></p>";
        echo "<b>Код помилки (errorCode):</b> " . $e->getCode() . "<br>";
        echo "<b>Детальна інформація (errorInfo):</b> " . print_r($pdo->errorInfo(), true) . "<br>";
        echo "<b>Повідомлення PDOException:</b> " . $e->getMessage() . "<br>";
        echo "</div>";
    }

    // Task 2: Пакет змін у межах транзакції
    echo "<h3>Завдання 2: Пакет змін у межах транзакції</h3>";
    try {
        $pdo->beginTransaction();
        $pdo->exec("UPDATE users SET name = 'Іван Петренко' WHERE email = 'ivan@example.com'");
        $pdo->exec("UPDATE users SET name = 'Марія Іванова' WHERE email = 'maria@example.com'");
        $pdo->commit();
        echo "<p>Транзакцію (оновлення записів) успішно виконано.</p>";
    } catch (PDOException $e) {
        $pdo->rollBack();
        echo "<p style='color:red;'>Помилка транзакції: " . $e->getMessage() . "</p>";
    }

    // Task 3: Повторювані вставки з підготовленими запитами
    echo "<h3>Завдання 3: Підготовлені запити (Prepared Statements)</h3>";
    try {
        $stmt = $pdo->prepare("INSERT INTO users (name, email) VALUES (:name, :email)");
        
        $newUsers = [
            ['name' => 'Олег', 'email' => 'oleg@test.com'],
            ['name' => 'Анна', 'email' => 'anna@test.com'],
            ['name' => 'Тарас', 'email' => 'taras@test.com']
        ];
        
        $count = 0;
        foreach ($newUsers as $user) {
            $stmt->execute([':name' => $user['name'], ':email' => $user['email']]);
            $count++;
        }
        echo "<p>Успішно вставлено $count нових записів через підготовлені запити.</p>";
        
    } catch (PDOException $e) {
        echo "<p style='color:red;'>Помилка: " . $e->getMessage() . "</p>";
    }
}

// Task 6: Перетворення рядків та файлів до формату HTML та навпаки (регулярні вирази)
echo "<h3>Завдання 6: Перетворення HTML <-> Текст (Регулярні вирази)</h3>";

// 1. String to HTML
$text = "Це заголовок\nА це звичайний текст із **жирним** виділенням.";
echo "<b>Оригінальний текст:</b> <pre>$text</pre>";

// Перетворюємо **текст** на <b>текст</b>
$html = preg_replace('/\*\*(.*?)\*\*/s', '<b>$1</b>', $text);
// Перетворюємо нові рядки на <br>
$html = preg_replace('/\n/', '<br>', $html);
echo "<b>Текст -> HTML:</b> <div style='border:1px solid #ccc; padding:5px;'>$html</div>";

// 2. HTML to String
// Видаляємо теги <br> (замінюємо на \n) та <b> (замінюємо на **)
$backToText = preg_replace('/<br\s*\/?>/i', "\n", $html);
$backToText = preg_replace('/<b>(.*?)<\/b>/i', '**$1**', $backToText);
echo "<b>HTML -> Текст:</b> <pre>$backToText</pre>";


// Task 7: Перевірка email за допомогою регулярних виразів
echo "<h3>Завдання 7: Перевірка e-mail</h3>";
$emailsToTest = [
    'valid.email@example.com',
    'invalid-email.com',
    'user@domain.co.uk',
    '@missinguser.com'
];

$emailPattern = '/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/';

echo "<ul>";
foreach ($emailsToTest as $email) {
    if (preg_match($emailPattern, $email)) {
        echo "<li><span style='color:green'>$email - Коректний</span></li>";
    } else {
        echo "<li><span style='color:red'>$email - Некоректний</span></li>";
    }
}
echo "</ul>";

?>
