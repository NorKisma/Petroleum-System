-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: 127.0.0.1    Database: pet_db
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `assets`
--

DROP TABLE IF EXISTS `assets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `value` float NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `purchase_date` datetime DEFAULT NULL,
  `depreciation_method` varchar(50) DEFAULT NULL,
  `useful_life_years` int(11) DEFAULT NULL,
  `salvage_value` float DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `assets_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assets`
--

LOCK TABLES `assets` WRITE;
/*!40000 ALTER TABLE `assets` DISABLE KEYS */;
/*!40000 ALTER TABLE `assets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `audit_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `module` varchar(50) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `audit_logs_ibfk_2` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES (1,1,'Login',NULL,'User logged in from 127.0.0.1',NULL,1,'2026-08-12 10:34:44'),(2,1,'Login',NULL,'User logged in from 127.0.0.1',NULL,1,'2026-08-12 10:35:20'),(3,1,'Login',NULL,'User logged in from 127.0.0.1',NULL,1,'2026-08-12 10:36:35'),(4,1,'CREATE','PETROLEUM','Fleet customer added: bashir','127.0.0.1',1,'2026-08-12 14:23:19');
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bank_accounts`
--

DROP TABLE IF EXISTS `bank_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bank_accounts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `account_name` varchar(100) NOT NULL,
  `account_number` varchar(50) DEFAULT NULL,
  `initial_balance` float DEFAULT NULL,
  `branch_id` int(11) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `branch_id` (`branch_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `bank_accounts_ibfk_1` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `bank_accounts_ibfk_2` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bank_accounts`
--

LOCK TABLES `bank_accounts` WRITE;
/*!40000 ALTER TABLE `bank_accounts` DISABLE KEYS */;
/*!40000 ALTER TABLE `bank_accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bank_transfers`
--

DROP TABLE IF EXISTS `bank_transfers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bank_transfers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_account_id` int(11) NOT NULL,
  `to_account_id` int(11) NOT NULL,
  `amount` float NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `transfer_date` datetime DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `from_account_id` (`from_account_id`),
  KEY `to_account_id` (`to_account_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `bank_transfers_ibfk_1` FOREIGN KEY (`from_account_id`) REFERENCES `chart_accounts` (`id`),
  CONSTRAINT `bank_transfers_ibfk_2` FOREIGN KEY (`to_account_id`) REFERENCES `chart_accounts` (`id`),
  CONSTRAINT `bank_transfers_ibfk_3` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bank_transfers`
--

LOCK TABLES `bank_transfers` WRITE;
/*!40000 ALTER TABLE `bank_transfers` DISABLE KEYS */;
/*!40000 ALTER TABLE `bank_transfers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `branches`
--

DROP TABLE IF EXISTS `branches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `branches` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `location` varchar(200) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `branches_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `branches`
--

LOCK TABLES `branches` WRITE;
/*!40000 ALTER TABLE `branches` DISABLE KEYS */;
/*!40000 ALTER TABLE `branches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `brands`
--

DROP TABLE IF EXISTS `brands`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `brands` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `tenant_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `brands_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brands`
--

LOCK TABLES `brands` WRITE;
/*!40000 ALTER TABLE `brands` DISABLE KEYS */;
/*!40000 ALTER TABLE `brands` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `tenant_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chart_accounts`
--

DROP TABLE IF EXISTS `chart_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chart_accounts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `account_code` varchar(20) NOT NULL,
  `account_name` varchar(100) NOT NULL,
  `category` varchar(50) NOT NULL,
  `sub_category` varchar(100) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `chart_accounts_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chart_accounts`
--

LOCK TABLES `chart_accounts` WRITE;
/*!40000 ALTER TABLE `chart_accounts` DISABLE KEYS */;
INSERT INTO `chart_accounts` VALUES (1,'1000','Cash in Hand','ASSETS','Bank Accounts',NULL,1,1,'2026-08-12 09:49:37'),(2,'1010','Bank Account','ASSETS','Bank Accounts',NULL,1,1,'2026-08-12 09:49:37'),(3,'1020','EVC Plus','ASSETS','Bank Accounts',NULL,1,1,'2026-08-12 09:49:37'),(4,'1030','eDahab','ASSETS','Bank Accounts',NULL,1,1,'2026-08-12 09:49:37'),(5,'1100','Accounts Receivable','ASSETS','Current Assets',NULL,1,1,'2026-08-12 09:49:37'),(6,'1200','Inventory','ASSETS','Current Assets',NULL,1,1,'2026-08-12 09:49:37'),(7,'1500','Fixed Assets','ASSETS','Non-Current Assets',NULL,1,1,'2026-08-12 09:49:37'),(8,'2000','Accounts Payable','LIABILITIES','Current Liabilities',NULL,1,1,'2026-08-12 09:49:37'),(9,'2100','Sales Tax Payable','LIABILITIES','Current Liabilities',NULL,1,1,'2026-08-12 09:49:38'),(10,'2500','Long Term Loans','LIABILITIES','Non-Current Liabilities',NULL,1,1,'2026-08-12 09:49:38'),(11,'3000','Owner\'s Equity','EQUITY','Equity',NULL,1,1,'2026-08-12 09:49:38'),(12,'3100','Retained Earnings','EQUITY','Equity',NULL,1,1,'2026-08-12 09:49:38'),(13,'4000','Sales Revenue','REVENUE','Operating Revenue',NULL,1,1,'2026-08-12 09:49:38'),(14,'4100','Service Revenue','REVENUE','Operating Revenue',NULL,1,1,'2026-08-12 09:49:38'),(15,'4500','Other Income','REVENUE','Other Revenue',NULL,1,1,'2026-08-12 09:49:38'),(16,'5000','Cost of Goods Sold','EXPENSES','Direct Expenses',NULL,1,1,'2026-08-12 09:49:38'),(17,'5100','Salaries & Wages','EXPENSES','Operating Expenses',NULL,1,1,'2026-08-12 09:49:38'),(18,'5200','Rent Expense','EXPENSES','Operating Expenses',NULL,1,1,'2026-08-12 09:49:38'),(19,'5300','Utilities (Electricity/Water)','EXPENSES','Operating Expenses',NULL,1,1,'2026-08-12 09:49:38'),(20,'5400','Marketing & Advertising','EXPENSES','Operating Expenses',NULL,1,1,'2026-08-12 09:49:38'),(21,'5500','Office Supplies','EXPENSES','Operating Expenses',NULL,1,1,'2026-08-12 09:49:38'),(22,'5600','Maintenance & Repairs','EXPENSES','Operating Expenses',NULL,1,1,'2026-08-12 09:49:38');
/*!40000 ALTER TABLE `chart_accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_groups`
--

DROP TABLE IF EXISTS `customer_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `customer_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `calculation_percentage` float DEFAULT NULL,
  `selling_price_group` varchar(100) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `customer_groups_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_groups`
--

LOCK TABLES `customer_groups` WRITE;
/*!40000 ALTER TABLE `customer_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `customer_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_payments`
--

DROP TABLE IF EXISTS `customer_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `customer_payments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `customer_id` int(11) DEFAULT NULL,
  `amount` float NOT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `reference_no` varchar(100) DEFAULT NULL,
  `payment_date` datetime DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `customer_payments_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `customer_payments_ibfk_2` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_payments`
--

LOCK TABLES `customer_payments` WRITE;
/*!40000 ALTER TABLE `customer_payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `customer_payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `customers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `customer_group_id` int(11) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_group_id` (`customer_group_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `customers_ibfk_1` FOREIGN KEY (`customer_group_id`) REFERENCES `customer_groups` (`id`),
  CONSTRAINT `customers_ibfk_2` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (1,'bashir','999999999',NULL,NULL,NULL,1,'2026-08-12 14:23:15');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `expenses`
--

DROP TABLE IF EXISTS `expenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `expenses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(200) NOT NULL,
  `amount` float NOT NULL,
  `category` varchar(50) NOT NULL,
  `payment_account` varchar(50) DEFAULT NULL,
  `branch_id` int(11) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `fuel_shift_id` int(11) DEFAULT NULL,
  `fuel_day_close_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `branch_id` (`branch_id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `fuel_shift_id` (`fuel_shift_id`),
  KEY `fuel_day_close_id` (`fuel_day_close_id`),
  CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `expenses_ibfk_2` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`),
  CONSTRAINT `expenses_ibfk_3` FOREIGN KEY (`fuel_shift_id`) REFERENCES `fuel_shifts` (`id`),
  CONSTRAINT `expenses_ibfk_4` FOREIGN KEY (`fuel_day_close_id`) REFERENCES `fuel_day_closes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expenses`
--

LOCK TABLES `expenses` WRITE;
/*!40000 ALTER TABLE `expenses` DISABLE KEYS */;
/*!40000 ALTER TABLE `expenses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fleet_profiles`
--

DROP TABLE IF EXISTS `fleet_profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fleet_profiles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `customer_id` int(11) NOT NULL,
  `fleet_code` varchar(50) DEFAULT NULL,
  `credit_limit` float DEFAULT NULL,
  `current_balance` float DEFAULT NULL,
  `payment_terms_days` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fleet_profiles_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `fleet_profiles_ibfk_2` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fleet_profiles`
--

LOCK TABLES `fleet_profiles` WRITE;
/*!40000 ALTER TABLE `fleet_profiles` DISABLE KEYS */;
INSERT INTO `fleet_profiles` VALUES (1,1,'',50000,0,30,1,1,'2026-08-12 14:23:17');
/*!40000 ALTER TABLE `fleet_profiles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_day_closes`
--

DROP TABLE IF EXISTS `fuel_day_closes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_day_closes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `close_date` date NOT NULL,
  `branch_id` int(11) DEFAULT NULL,
  `total_sales_liters` float DEFAULT NULL,
  `total_sales_amount` float DEFAULT NULL,
  `total_deliveries_liters` float DEFAULT NULL,
  `total_variance` float DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `closed_by` int(11) NOT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `branch_id` (`branch_id`),
  KEY `closed_by` (`closed_by`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_day_closes_ibfk_1` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `fuel_day_closes_ibfk_2` FOREIGN KEY (`closed_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_day_closes_ibfk_3` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_day_closes`
--

LOCK TABLES `fuel_day_closes` WRITE;
/*!40000 ALTER TABLE `fuel_day_closes` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_day_closes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_deliveries`
--

DROP TABLE IF EXISTS `fuel_deliveries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_deliveries` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `delivery_no` varchar(50) NOT NULL,
  `vendor_id` int(11) DEFAULT NULL,
  `purchase_name` varchar(200) DEFAULT NULL,
  `fuel_type_id` int(11) NOT NULL,
  `tank_id` int(11) NOT NULL,
  `liters_received` float NOT NULL,
  `unit_cost` float NOT NULL,
  `total_cost` float NOT NULL,
  `waybill_no` varchar(100) DEFAULT NULL,
  `driver_name` varchar(100) DEFAULT NULL,
  `vehicle_no` varchar(50) DEFAULT NULL,
  `before_dip` float DEFAULT NULL,
  `after_dip` float DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `branch_id` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `payment_method` varchar(20) DEFAULT NULL,
  `is_locked` tinyint(1) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `delivery_date` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `vendor_id` (`vendor_id`),
  KEY `fuel_type_id` (`fuel_type_id`),
  KEY `tank_id` (`tank_id`),
  KEY `user_id` (`user_id`),
  KEY `branch_id` (`branch_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_deliveries_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`id`),
  CONSTRAINT `fuel_deliveries_ibfk_2` FOREIGN KEY (`fuel_type_id`) REFERENCES `fuel_types` (`id`),
  CONSTRAINT `fuel_deliveries_ibfk_3` FOREIGN KEY (`tank_id`) REFERENCES `fuel_tanks` (`id`),
  CONSTRAINT `fuel_deliveries_ibfk_4` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_deliveries_ibfk_5` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `fuel_deliveries_ibfk_6` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_deliveries`
--

LOCK TABLES `fuel_deliveries` WRITE;
/*!40000 ALTER TABLE `fuel_deliveries` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_deliveries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_dip_readings`
--

DROP TABLE IF EXISTS `fuel_dip_readings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_dip_readings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tank_id` int(11) NOT NULL,
  `reading_liters` float NOT NULL,
  `book_stock` float NOT NULL,
  `variance` float DEFAULT NULL,
  `reading_type` varchar(20) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `branch_id` int(11) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `reading_date` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tank_id` (`tank_id`),
  KEY `user_id` (`user_id`),
  KEY `branch_id` (`branch_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_dip_readings_ibfk_1` FOREIGN KEY (`tank_id`) REFERENCES `fuel_tanks` (`id`),
  CONSTRAINT `fuel_dip_readings_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_dip_readings_ibfk_3` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `fuel_dip_readings_ibfk_4` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_dip_readings`
--

LOCK TABLES `fuel_dip_readings` WRITE;
/*!40000 ALTER TABLE `fuel_dip_readings` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_dip_readings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_losses`
--

DROP TABLE IF EXISTS `fuel_losses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_losses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `log_date` date NOT NULL,
  `fuel_type_id` int(11) NOT NULL,
  `tank_id` int(11) NOT NULL,
  `liters_lost` float NOT NULL,
  `loss_type` varchar(50) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `recorded_by` int(11) NOT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fuel_type_id` (`fuel_type_id`),
  KEY `tank_id` (`tank_id`),
  KEY `recorded_by` (`recorded_by`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_losses_ibfk_1` FOREIGN KEY (`fuel_type_id`) REFERENCES `fuel_types` (`id`),
  CONSTRAINT `fuel_losses_ibfk_2` FOREIGN KEY (`tank_id`) REFERENCES `fuel_tanks` (`id`),
  CONSTRAINT `fuel_losses_ibfk_3` FOREIGN KEY (`recorded_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_losses_ibfk_4` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_losses`
--

LOCK TABLES `fuel_losses` WRITE;
/*!40000 ALTER TABLE `fuel_losses` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_losses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_price_history`
--

DROP TABLE IF EXISTS `fuel_price_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_price_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fuel_type_id` int(11) NOT NULL,
  `old_buy_price` float NOT NULL,
  `new_buy_price` float NOT NULL,
  `old_sell_price` float NOT NULL,
  `new_sell_price` float NOT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `changed_by` int(11) NOT NULL,
  `tenant_id` int(11) NOT NULL,
  `effective_date` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fuel_type_id` (`fuel_type_id`),
  KEY `changed_by` (`changed_by`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_price_history_ibfk_1` FOREIGN KEY (`fuel_type_id`) REFERENCES `fuel_types` (`id`),
  CONSTRAINT `fuel_price_history_ibfk_2` FOREIGN KEY (`changed_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_price_history_ibfk_3` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_price_history`
--

LOCK TABLES `fuel_price_history` WRITE;
/*!40000 ALTER TABLE `fuel_price_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_price_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_pump_daily_logs`
--

DROP TABLE IF EXISTS `fuel_pump_daily_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_pump_daily_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pump_id` int(11) NOT NULL,
  `log_date` date NOT NULL,
  `opening_meter` float DEFAULT NULL,
  `closing_meter` float DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `pump_id` (`pump_id`),
  KEY `user_id` (`user_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_pump_daily_logs_ibfk_1` FOREIGN KEY (`pump_id`) REFERENCES `fuel_pumps` (`id`),
  CONSTRAINT `fuel_pump_daily_logs_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_pump_daily_logs_ibfk_3` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_pump_daily_logs`
--

LOCK TABLES `fuel_pump_daily_logs` WRITE;
/*!40000 ALTER TABLE `fuel_pump_daily_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_pump_daily_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_pump_shift_logs`
--

DROP TABLE IF EXISTS `fuel_pump_shift_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_pump_shift_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pump_id` int(11) NOT NULL,
  `log_date` date NOT NULL,
  `shift_number` int(11) NOT NULL,
  `opening_meter` float DEFAULT NULL,
  `closing_meter` float DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `attendant_id` int(11) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_fuel_pump_shift_log` (`pump_id`,`log_date`,`shift_number`,`tenant_id`),
  KEY `user_id` (`user_id`),
  KEY `attendant_id` (`attendant_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_pump_shift_logs_ibfk_1` FOREIGN KEY (`pump_id`) REFERENCES `fuel_pumps` (`id`),
  CONSTRAINT `fuel_pump_shift_logs_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_pump_shift_logs_ibfk_3` FOREIGN KEY (`attendant_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_pump_shift_logs_ibfk_4` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_pump_shift_logs`
--

LOCK TABLES `fuel_pump_shift_logs` WRITE;
/*!40000 ALTER TABLE `fuel_pump_shift_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_pump_shift_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_pumps`
--

DROP TABLE IF EXISTS `fuel_pumps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_pumps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pump_number` varchar(50) NOT NULL,
  `selling_price` float DEFAULT NULL,
  `fuel_type_id` int(11) NOT NULL,
  `tank_id` int(11) NOT NULL,
  `branch_id` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fuel_type_id` (`fuel_type_id`),
  KEY `tank_id` (`tank_id`),
  KEY `branch_id` (`branch_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_pumps_ibfk_1` FOREIGN KEY (`fuel_type_id`) REFERENCES `fuel_types` (`id`),
  CONSTRAINT `fuel_pumps_ibfk_2` FOREIGN KEY (`tank_id`) REFERENCES `fuel_tanks` (`id`),
  CONSTRAINT `fuel_pumps_ibfk_3` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `fuel_pumps_ibfk_4` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_pumps`
--

LOCK TABLES `fuel_pumps` WRITE;
/*!40000 ALTER TABLE `fuel_pumps` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_pumps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_sales`
--

DROP TABLE IF EXISTS `fuel_sales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_sales` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `invoice_no` varchar(50) NOT NULL,
  `pump_id` int(11) DEFAULT NULL,
  `fuel_type_id` int(11) NOT NULL,
  `tank_id` int(11) NOT NULL,
  `liters_sold` float NOT NULL,
  `unit_price` float NOT NULL,
  `total_amount` float NOT NULL,
  `payment_method` varchar(20) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `fleet_profile_id` int(11) DEFAULT NULL,
  `vehicle_plate` varchar(50) DEFAULT NULL,
  `driver_name` varchar(100) DEFAULT NULL,
  `meter_before` float DEFAULT NULL,
  `meter_after` float DEFAULT NULL,
  `attendant_id` int(11) DEFAULT NULL,
  `branch_id` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `shift_number` int(11) DEFAULT NULL,
  `fuel_shift_id` int(11) DEFAULT NULL,
  `is_locked` tinyint(1) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `sale_date` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `pump_id` (`pump_id`),
  KEY `fuel_type_id` (`fuel_type_id`),
  KEY `tank_id` (`tank_id`),
  KEY `customer_id` (`customer_id`),
  KEY `fleet_profile_id` (`fleet_profile_id`),
  KEY `attendant_id` (`attendant_id`),
  KEY `branch_id` (`branch_id`),
  KEY `fuel_shift_id` (`fuel_shift_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_sales_ibfk_1` FOREIGN KEY (`pump_id`) REFERENCES `fuel_pumps` (`id`),
  CONSTRAINT `fuel_sales_ibfk_2` FOREIGN KEY (`fuel_type_id`) REFERENCES `fuel_types` (`id`),
  CONSTRAINT `fuel_sales_ibfk_3` FOREIGN KEY (`tank_id`) REFERENCES `fuel_tanks` (`id`),
  CONSTRAINT `fuel_sales_ibfk_4` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `fuel_sales_ibfk_5` FOREIGN KEY (`fleet_profile_id`) REFERENCES `fleet_profiles` (`id`),
  CONSTRAINT `fuel_sales_ibfk_6` FOREIGN KEY (`attendant_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_sales_ibfk_7` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `fuel_sales_ibfk_8` FOREIGN KEY (`fuel_shift_id`) REFERENCES `fuel_shifts` (`id`),
  CONSTRAINT `fuel_sales_ibfk_9` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_sales`
--

LOCK TABLES `fuel_sales` WRITE;
/*!40000 ALTER TABLE `fuel_sales` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_sales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_shifts`
--

DROP TABLE IF EXISTS `fuel_shifts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_shifts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `log_date` date NOT NULL,
  `shift_number` int(11) NOT NULL,
  `attendant_id` int(11) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `summary_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`summary_data`)),
  `notes` text DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `closed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_fuel_shift` (`log_date`,`shift_number`,`tenant_id`),
  KEY `attendant_id` (`attendant_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_shifts_ibfk_1` FOREIGN KEY (`attendant_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_shifts_ibfk_2` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_shifts`
--

LOCK TABLES `fuel_shifts` WRITE;
/*!40000 ALTER TABLE `fuel_shifts` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_shifts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_stock_ledger`
--

DROP TABLE IF EXISTS `fuel_stock_ledger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_stock_ledger` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fuel_type_id` int(11) NOT NULL,
  `tank_id` int(11) NOT NULL,
  `transaction_type` varchar(30) NOT NULL,
  `reference_id` int(11) DEFAULT NULL,
  `reference_no` varchar(50) DEFAULT NULL,
  `liters_in` float DEFAULT NULL,
  `liters_out` float DEFAULT NULL,
  `balance_after` float NOT NULL,
  `unit_cost` float DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fuel_type_id` (`fuel_type_id`),
  KEY `tank_id` (`tank_id`),
  KEY `user_id` (`user_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_stock_ledger_ibfk_1` FOREIGN KEY (`fuel_type_id`) REFERENCES `fuel_types` (`id`),
  CONSTRAINT `fuel_stock_ledger_ibfk_2` FOREIGN KEY (`tank_id`) REFERENCES `fuel_tanks` (`id`),
  CONSTRAINT `fuel_stock_ledger_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fuel_stock_ledger_ibfk_4` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_stock_ledger`
--

LOCK TABLES `fuel_stock_ledger` WRITE;
/*!40000 ALTER TABLE `fuel_stock_ledger` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_stock_ledger` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_tanks`
--

DROP TABLE IF EXISTS `fuel_tanks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_tanks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `fuel_type_id` int(11) NOT NULL,
  `branch_id` int(11) DEFAULT NULL,
  `capacity_liters` float NOT NULL,
  `current_level` float DEFAULT NULL,
  `min_alert_level` float DEFAULT NULL,
  `last_dip_reading` float DEFAULT NULL,
  `last_dip_date` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fuel_type_id` (`fuel_type_id`),
  KEY `branch_id` (`branch_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_tanks_ibfk_1` FOREIGN KEY (`fuel_type_id`) REFERENCES `fuel_types` (`id`),
  CONSTRAINT `fuel_tanks_ibfk_2` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `fuel_tanks_ibfk_3` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_tanks`
--

LOCK TABLES `fuel_tanks` WRITE;
/*!40000 ALTER TABLE `fuel_tanks` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_tanks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fuel_types`
--

DROP TABLE IF EXISTS `fuel_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fuel_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(20) NOT NULL,
  `color_code` varchar(20) DEFAULT NULL,
  `buy_price` float DEFAULT NULL,
  `sell_price` float DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `fuel_types_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fuel_types`
--

LOCK TABLES `fuel_types` WRITE;
/*!40000 ALTER TABLE `fuel_types` DISABLE KEYS */;
/*!40000 ALTER TABLE `fuel_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `journal_entries`
--

DROP TABLE IF EXISTS `journal_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `journal_entries` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reference` varchar(50) NOT NULL,
  `date` datetime DEFAULT NULL,
  `description` text DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `journal_entries_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journal_entries`
--

LOCK TABLES `journal_entries` WRITE;
/*!40000 ALTER TABLE `journal_entries` DISABLE KEYS */;
/*!40000 ALTER TABLE `journal_entries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `journal_lines`
--

DROP TABLE IF EXISTS `journal_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `journal_lines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entry_id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `debit` float DEFAULT NULL,
  `credit` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `entry_id` (`entry_id`),
  KEY `account_id` (`account_id`),
  CONSTRAINT `journal_lines_ibfk_1` FOREIGN KEY (`entry_id`) REFERENCES `journal_entries` (`id`),
  CONSTRAINT `journal_lines_ibfk_2` FOREIGN KEY (`account_id`) REFERENCES `chart_accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journal_lines`
--

LOCK TABLES `journal_lines` WRITE;
/*!40000 ALTER TABLE `journal_lines` DISABLE KEYS */;
/*!40000 ALTER TABLE `journal_lines` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `other_incomes`
--

DROP TABLE IF EXISTS `other_incomes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `other_incomes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(200) DEFAULT NULL,
  `amount` float NOT NULL,
  `category` varchar(100) NOT NULL,
  `account` varchar(100) NOT NULL,
  `income_date` datetime DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `other_incomes_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `other_incomes`
--

LOCK TABLES `other_incomes` WRITE;
/*!40000 ALTER TABLE `other_incomes` DISABLE KEYS */;
/*!40000 ALTER TABLE `other_incomes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payroll`
--

DROP TABLE IF EXISTS `payroll`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payroll` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `amount` float NOT NULL,
  `month` varchar(20) NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `paid_date` datetime DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `fuel_shift_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `fuel_shift_id` (`fuel_shift_id`),
  CONSTRAINT `payroll_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `payroll_ibfk_2` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`),
  CONSTRAINT `payroll_ibfk_3` FOREIGN KEY (`fuel_shift_id`) REFERENCES `fuel_shifts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payroll`
--

LOCK TABLES `payroll` WRITE;
/*!40000 ALTER TABLE `payroll` DISABLE KEYS */;
/*!40000 ALTER TABLE `payroll` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `barcode` varchar(50) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `buy_price` float DEFAULT NULL,
  `sell_price` float DEFAULT NULL,
  `stock_quantity` int(11) DEFAULT NULL,
  `low_stock_threshold` float DEFAULT NULL,
  `category_id` int(11) DEFAULT NULL,
  `unit_id` int(11) DEFAULT NULL,
  `brand_id` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `barcode` (`barcode`),
  KEY `category_id` (`category_id`),
  KEY `unit_id` (`unit_id`),
  KEY `brand_id` (`brand_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `products_ibfk_2` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`),
  CONSTRAINT `products_ibfk_3` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`id`),
  CONSTRAINT `products_ibfk_4` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_items`
--

DROP TABLE IF EXISTS `purchase_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `purchase_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `purchase_id` int(11) NOT NULL,
  `product_id` int(11) DEFAULT NULL,
  `product_name` varchar(100) DEFAULT NULL,
  `quantity` int(11) NOT NULL,
  `unit_cost` float NOT NULL,
  `selling_price` float DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `purchase_id` (`purchase_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `purchase_items_ibfk_1` FOREIGN KEY (`purchase_id`) REFERENCES `purchases` (`id`),
  CONSTRAINT `purchase_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_items`
--

LOCK TABLES `purchase_items` WRITE;
/*!40000 ALTER TABLE `purchase_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_return_items`
--

DROP TABLE IF EXISTS `purchase_return_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `purchase_return_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `purchase_return_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit_cost` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `purchase_return_id` (`purchase_return_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `purchase_return_items_ibfk_1` FOREIGN KEY (`purchase_return_id`) REFERENCES `purchase_returns` (`id`),
  CONSTRAINT `purchase_return_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_return_items`
--

LOCK TABLES `purchase_return_items` WRITE;
/*!40000 ALTER TABLE `purchase_return_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase_return_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_returns`
--

DROP TABLE IF EXISTS `purchase_returns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `purchase_returns` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `purchase_id` int(11) NOT NULL,
  `invoice_no` varchar(50) NOT NULL,
  `total_amount` float NOT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `purchase_id` (`purchase_id`),
  KEY `user_id` (`user_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `purchase_returns_ibfk_1` FOREIGN KEY (`purchase_id`) REFERENCES `purchases` (`id`),
  CONSTRAINT `purchase_returns_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `purchase_returns_ibfk_3` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_returns`
--

LOCK TABLES `purchase_returns` WRITE;
/*!40000 ALTER TABLE `purchase_returns` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase_returns` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchases`
--

DROP TABLE IF EXISTS `purchases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `purchases` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `invoice_no` varchar(50) NOT NULL,
  `total_amount` float NOT NULL,
  `payment_method` varchar(20) DEFAULT NULL,
  `ap_account` varchar(100) DEFAULT NULL,
  `vendor_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `branch_id` int(11) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `attachment` varchar(255) DEFAULT NULL,
  `purchase_date` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `vendor_id` (`vendor_id`),
  KEY `user_id` (`user_id`),
  KEY `branch_id` (`branch_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `purchases_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`id`),
  CONSTRAINT `purchases_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `purchases_ibfk_3` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `purchases_ibfk_4` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchases`
--

LOCK TABLES `purchases` WRITE;
/*!40000 ALTER TABLE `purchases` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `permissions` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`permissions`)),
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `roles_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `saas_payments`
--

DROP TABLE IF EXISTS `saas_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `saas_payments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tenant_id` int(11) NOT NULL,
  `amount` float NOT NULL,
  `payment_date` datetime DEFAULT NULL,
  `billing_period` varchar(50) DEFAULT NULL,
  `reference_no` varchar(100) DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `saas_payments_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `saas_payments`
--

LOCK TABLES `saas_payments` WRITE;
/*!40000 ALTER TABLE `saas_payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `saas_payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sale_items`
--

DROP TABLE IF EXISTS `sale_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sale_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sale_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit_price` float NOT NULL,
  `buy_price` float NOT NULL,
  `size` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sale_id` (`sale_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `sale_items_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`id`),
  CONSTRAINT `sale_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sale_items`
--

LOCK TABLES `sale_items` WRITE;
/*!40000 ALTER TABLE `sale_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `sale_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sale_return_items`
--

DROP TABLE IF EXISTS `sale_return_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sale_return_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sale_return_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit_price` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sale_return_id` (`sale_return_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `sale_return_items_ibfk_1` FOREIGN KEY (`sale_return_id`) REFERENCES `sale_returns` (`id`),
  CONSTRAINT `sale_return_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sale_return_items`
--

LOCK TABLES `sale_return_items` WRITE;
/*!40000 ALTER TABLE `sale_return_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `sale_return_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sale_returns`
--

DROP TABLE IF EXISTS `sale_returns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sale_returns` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sale_id` int(11) NOT NULL,
  `invoice_no` varchar(50) NOT NULL,
  `total_amount` float NOT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sale_id` (`sale_id`),
  KEY `user_id` (`user_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `sale_returns_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`id`),
  CONSTRAINT `sale_returns_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `sale_returns_ibfk_3` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sale_returns`
--

LOCK TABLES `sale_returns` WRITE;
/*!40000 ALTER TABLE `sale_returns` DISABLE KEYS */;
/*!40000 ALTER TABLE `sale_returns` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sales`
--

DROP TABLE IF EXISTS `sales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sales` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `invoice_no` varchar(50) NOT NULL,
  `subtotal` float DEFAULT NULL,
  `tax_amount` float DEFAULT NULL,
  `discount_amount` float DEFAULT NULL,
  `total_amount` float NOT NULL,
  `payment_method` varchar(20) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `branch_id` int(11) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `attachment` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_no` (`invoice_no`),
  KEY `user_id` (`user_id`),
  KEY `customer_id` (`customer_id`),
  KEY `branch_id` (`branch_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `sales_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `sales_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `sales_ibfk_3` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `sales_ibfk_4` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sales`
--

LOCK TABLES `sales` WRITE;
/*!40000 ALTER TABLE `sales` DISABLE KEYS */;
/*!40000 ALTER TABLE `sales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `share_investments`
--

DROP TABLE IF EXISTS `share_investments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `share_investments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `shareholder_id` int(11) NOT NULL,
  `amount` float NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `investment_date` datetime DEFAULT NULL,
  `account_id` int(11) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `shareholder_id` (`shareholder_id`),
  KEY `account_id` (`account_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `share_investments_ibfk_1` FOREIGN KEY (`shareholder_id`) REFERENCES `shareholders` (`id`),
  CONSTRAINT `share_investments_ibfk_2` FOREIGN KEY (`account_id`) REFERENCES `chart_accounts` (`id`),
  CONSTRAINT `share_investments_ibfk_3` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `share_investments`
--

LOCK TABLES `share_investments` WRITE;
/*!40000 ALTER TABLE `share_investments` DISABLE KEYS */;
/*!40000 ALTER TABLE `share_investments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `share_withdrawals`
--

DROP TABLE IF EXISTS `share_withdrawals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `share_withdrawals` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `shareholder_id` int(11) NOT NULL,
  `amount` float NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `withdrawal_date` datetime DEFAULT NULL,
  `account_id` int(11) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `shareholder_id` (`shareholder_id`),
  KEY `account_id` (`account_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `share_withdrawals_ibfk_1` FOREIGN KEY (`shareholder_id`) REFERENCES `shareholders` (`id`),
  CONSTRAINT `share_withdrawals_ibfk_2` FOREIGN KEY (`account_id`) REFERENCES `chart_accounts` (`id`),
  CONSTRAINT `share_withdrawals_ibfk_3` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `share_withdrawals`
--

LOCK TABLES `share_withdrawals` WRITE;
/*!40000 ALTER TABLE `share_withdrawals` DISABLE KEYS */;
/*!40000 ALTER TABLE `share_withdrawals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shareholders`
--

DROP TABLE IF EXISTS `shareholders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `shareholders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `shareholders_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shareholders`
--

LOCK TABLES `shareholders` WRITE;
/*!40000 ALTER TABLE `shareholders` DISABLE KEYS */;
/*!40000 ALTER TABLE `shareholders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_adjustments`
--

DROP TABLE IF EXISTS `stock_adjustments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stock_adjustments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `type` varchar(50) NOT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `branch_id` int(11) DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  KEY `user_id` (`user_id`),
  KEY `branch_id` (`branch_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `stock_adjustments_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `stock_adjustments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `stock_adjustments_ibfk_3` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `stock_adjustments_ibfk_4` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_adjustments`
--

LOCK TABLES `stock_adjustments` WRITE;
/*!40000 ALTER TABLE `stock_adjustments` DISABLE KEYS */;
/*!40000 ALTER TABLE `stock_adjustments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_transfer_items`
--

DROP TABLE IF EXISTS `stock_transfer_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stock_transfer_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `transfer_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit_price` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `transfer_id` (`transfer_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `stock_transfer_items_ibfk_1` FOREIGN KEY (`transfer_id`) REFERENCES `stock_transfers` (`id`),
  CONSTRAINT `stock_transfer_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_transfer_items`
--

LOCK TABLES `stock_transfer_items` WRITE;
/*!40000 ALTER TABLE `stock_transfer_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `stock_transfer_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_transfers`
--

DROP TABLE IF EXISTS `stock_transfers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stock_transfers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reference_no` varchar(50) NOT NULL,
  `from_branch_id` int(11) NOT NULL,
  `to_branch_id` int(11) NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `shipping_charges` float DEFAULT NULL,
  `additional_notes` text DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `from_branch_id` (`from_branch_id`),
  KEY `to_branch_id` (`to_branch_id`),
  KEY `user_id` (`user_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `stock_transfers_ibfk_1` FOREIGN KEY (`from_branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `stock_transfers_ibfk_2` FOREIGN KEY (`to_branch_id`) REFERENCES `branches` (`id`),
  CONSTRAINT `stock_transfers_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `stock_transfers_ibfk_4` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_transfers`
--

LOCK TABLES `stock_transfers` WRITE;
/*!40000 ALTER TABLE `stock_transfers` DISABLE KEYS */;
/*!40000 ALTER TABLE `stock_transfers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenants`
--

DROP TABLE IF EXISTS `tenants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenants` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `subdomain` varchar(50) DEFAULT NULL,
  `logo` varchar(200) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `slogan` varchar(255) DEFAULT NULL,
  `currency` varchar(100) DEFAULT NULL,
  `tax_rate` float DEFAULT NULL,
  `start_date` datetime DEFAULT NULL,
  `currency_symbol_placement` varchar(20) DEFAULT NULL,
  `currency_precision` int(11) DEFAULT NULL,
  `quantity_precision` int(11) DEFAULT NULL,
  `number_display_format` varchar(20) DEFAULT NULL,
  `default_profit_percent` float DEFAULT NULL,
  `stock_accounting_method` varchar(20) DEFAULT NULL,
  `financial_year_start_month` varchar(20) DEFAULT NULL,
  `transaction_edit_days` int(11) DEFAULT NULL,
  `timezone` varchar(100) DEFAULT NULL,
  `date_format` varchar(50) DEFAULT NULL,
  `time_format` varchar(20) DEFAULT NULL,
  `sku_prefix` varchar(10) DEFAULT NULL,
  `enable_product_expiry` tinyint(1) DEFAULT NULL,
  `expiry_action` varchar(20) DEFAULT NULL,
  `stock_expiry_alert_days` int(11) DEFAULT NULL,
  `enable_batch_number` tinyint(1) DEFAULT NULL,
  `pos_shortcuts` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`pos_shortcuts`)),
  `disable_checkout_button` tinyint(1) DEFAULT NULL,
  `enable_drafts` tinyint(1) DEFAULT NULL,
  `pos_disable_discount` tinyint(1) DEFAULT NULL,
  `pos_disable_tax` tinyint(1) DEFAULT NULL,
  `pos_subtotal_editable` tinyint(1) DEFAULT NULL,
  `pos_disable_multiple_pay` tinyint(1) DEFAULT NULL,
  `pos_disable_express_checkout` tinyint(1) DEFAULT NULL,
  `pos_dont_show_product_suggestion` tinyint(1) DEFAULT NULL,
  `pos_dont_show_recent_transactions` tinyint(1) DEFAULT NULL,
  `pos_disable_suspend_sale` tinyint(1) DEFAULT NULL,
  `pos_enable_transaction_date` tinyint(1) DEFAULT NULL,
  `pos_is_service_staff_required` tinyint(1) DEFAULT NULL,
  `pos_disable_credit_sale_button` tinyint(1) DEFAULT NULL,
  `pos_enable_weighing_scale` tinyint(1) DEFAULT NULL,
  `order_prefix` varchar(10) DEFAULT NULL,
  `email_host` varchar(100) DEFAULT NULL,
  `email_port` int(11) DEFAULT NULL,
  `email_user` varchar(100) DEFAULT NULL,
  `email_pass` varchar(100) DEFAULT NULL,
  `email_from_name` varchar(100) DEFAULT NULL,
  `email_from_address` varchar(100) DEFAULT NULL,
  `email_encryption` varchar(10) DEFAULT NULL,
  `subscription_plan` varchar(20) DEFAULT NULL,
  `subscription_expiry` datetime DEFAULT NULL,
  `monthly_fee` float DEFAULT NULL,
  `subscription_status` varchar(20) DEFAULT NULL,
  `subscription_balance` float DEFAULT NULL,
  `last_payment_date` datetime DEFAULT NULL,
  `last_billing_date` datetime DEFAULT NULL,
  `module_pos` tinyint(1) DEFAULT NULL,
  `module_inventory` tinyint(1) DEFAULT NULL,
  `module_accounting` tinyint(1) DEFAULT NULL,
  `module_share` tinyint(1) DEFAULT NULL,
  `module_sales` tinyint(1) DEFAULT NULL,
  `module_purchases` tinyint(1) DEFAULT NULL,
  `module_customers` tinyint(1) DEFAULT NULL,
  `module_hrm` tinyint(1) DEFAULT NULL,
  `module_settings` tinyint(1) DEFAULT NULL,
  `module_expenses` tinyint(1) DEFAULT NULL,
  `module_stock_transfer` tinyint(1) DEFAULT NULL,
  `module_stock_adjustment` tinyint(1) DEFAULT NULL,
  `module_service_staff` tinyint(1) DEFAULT NULL,
  `module_bookings` tinyint(1) DEFAULT NULL,
  `module_add_sale` tinyint(1) DEFAULT NULL,
  `module_tables` tinyint(1) DEFAULT NULL,
  `module_modifiers` tinyint(1) DEFAULT NULL,
  `module_kitchen` tinyint(1) DEFAULT NULL,
  `module_subscription` tinyint(1) DEFAULT NULL,
  `module_types_of_service` tinyint(1) DEFAULT NULL,
  `module_crm` tinyint(1) DEFAULT NULL,
  `module_manufacturing` tinyint(1) DEFAULT NULL,
  `module_project` tinyint(1) DEFAULT NULL,
  `module_assets` tinyint(1) DEFAULT NULL,
  `module_repair` tinyint(1) DEFAULT NULL,
  `module_petroleum` tinyint(1) DEFAULT NULL,
  `petroleum_require_daily_dip` tinyint(1) DEFAULT NULL,
  `petroleum_variance_threshold` float DEFAULT NULL,
  `petroleum_require_vehicle_plate` tinyint(1) DEFAULT NULL,
  `petroleum_fleet_credit_enabled` tinyint(1) DEFAULT NULL,
  `petroleum_auto_morning_dip` tinyint(1) DEFAULT NULL,
  `petroleum_morning_auto_hour` int(11) DEFAULT NULL,
  `petroleum_morning_mode` varchar(20) DEFAULT NULL,
  `petroleum_shift1_name` varchar(100) DEFAULT NULL,
  `petroleum_shift1_attendant` varchar(100) DEFAULT NULL,
  `petroleum_shift1_start_hour` int(11) DEFAULT NULL,
  `petroleum_shift1_end_hour` int(11) DEFAULT NULL,
  `petroleum_shift2_name` varchar(100) DEFAULT NULL,
  `petroleum_shift2_attendant` varchar(100) DEFAULT NULL,
  `petroleum_shift2_start_hour` int(11) DEFAULT NULL,
  `petroleum_shift2_end_hour` int(11) DEFAULT NULL,
  `default_sale_discount` float DEFAULT NULL,
  `default_sale_tax` varchar(50) DEFAULT NULL,
  `sales_item_addition_method` varchar(50) DEFAULT NULL,
  `amount_rounding_method` varchar(50) DEFAULT NULL,
  `sales_price_is_minimum` tinyint(1) DEFAULT NULL,
  `allow_overselling` tinyint(1) DEFAULT NULL,
  `enable_sales_order` tinyint(1) DEFAULT NULL,
  `is_pay_term_required` tinyint(1) DEFAULT NULL,
  `sales_commission_agent` varchar(50) DEFAULT NULL,
  `commission_calculation_type` varchar(50) DEFAULT NULL,
  `is_commission_agent_required` tinyint(1) DEFAULT NULL,
  `enable_payment_link` tinyint(1) DEFAULT NULL,
  `razorpay_key_id` varchar(255) DEFAULT NULL,
  `razorpay_key_secret` varchar(255) DEFAULT NULL,
  `stripe_public_key` varchar(255) DEFAULT NULL,
  `stripe_secret_key` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subdomain` (`subdomain`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenants`
--

LOCK TABLES `tenants` WRITE;
/*!40000 ALTER TABLE `tenants` DISABLE KEYS */;
INSERT INTO `tenants` VALUES (1,'Rays Technology sulotions',NULL,'uploads/logos/logo_1_d.png',NULL,NULL,NULL,NULL,'USD',0,'2026-08-12 00:00:00','before',2,2,'full',25,'FIFO','January',30,'Africa/Muqdisho','dd/mm/yyyy','24 hour','SKU',0,'keep',30,1,NULL,0,1,0,0,1,0,0,0,0,0,1,0,0,0,'ORD','None',587,'None','None','None','None','tls','trial',NULL,0,'active',0,NULL,'2026-08-12 09:49:37',0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0.5,1,1,1,6,'automatic','Saaka (7AM-5PM)',NULL,7,17,'Habeen (5PM-7AM)',NULL,17,7,0,'','add_new','none',0,0,0,0,'disable','percentage',0,0,'None','None','None','None','2026-08-12 09:49:37');
/*!40000 ALTER TABLE `tenants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `units`
--

DROP TABLE IF EXISTS `units`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `units` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `tenant_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `units_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `units`
--

LOCK TABLES `units` WRITE;
/*!40000 ALTER TABLE `units` DISABLE KEYS */;
/*!40000 ALTER TABLE `units` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password` varchar(60) NOT NULL,
  `role` varchar(20) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `salary` float DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `branch_id` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_super_admin` tinyint(1) DEFAULT NULL,
  `otp_code` varchar(10) DEFAULT NULL,
  `otp_expiry` datetime DEFAULT NULL,
  `module_pos` tinyint(1) DEFAULT NULL,
  `module_inventory` tinyint(1) DEFAULT NULL,
  `module_accounting` tinyint(1) DEFAULT NULL,
  `module_share` tinyint(1) DEFAULT NULL,
  `module_sales` tinyint(1) DEFAULT NULL,
  `module_purchases` tinyint(1) DEFAULT NULL,
  `module_customers` tinyint(1) DEFAULT NULL,
  `module_staff` tinyint(1) DEFAULT NULL,
  `module_settings` tinyint(1) DEFAULT NULL,
  `module_petroleum` tinyint(1) DEFAULT NULL,
  `module_expenses` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `tenant_id` (`tenant_id`),
  KEY `branch_id` (`branch_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`),
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`branch_id`) REFERENCES `branches` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'raystech','raystechcenter@gmail.com','$2b$12$J7M3KFkWAD48cpUnT4SBH.plqlflR9WXPEtEHbT5LUccbtgURIuVu','admin',NULL,0,1,NULL,1,1,NULL,NULL,1,1,1,1,1,1,1,1,1,0,1,'2026-08-12 09:49:37');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vendor_payments`
--

DROP TABLE IF EXISTS `vendor_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vendor_payments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vendor_id` int(11) NOT NULL,
  `amount` float NOT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `reference_no` varchar(100) DEFAULT NULL,
  `payment_date` datetime DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `vendor_id` (`vendor_id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `vendor_payments_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`id`),
  CONSTRAINT `vendor_payments_ibfk_2` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vendor_payments`
--

LOCK TABLES `vendor_payments` WRITE;
/*!40000 ALTER TABLE `vendor_payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `vendor_payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vendors`
--

DROP TABLE IF EXISTS `vendors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vendors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `tenant_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  CONSTRAINT `vendors_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vendors`
--

LOCK TABLES `vendors` WRITE;
/*!40000 ALTER TABLE `vendors` DISABLE KEYS */;
/*!40000 ALTER TABLE `vendors` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-13  6:33:22
