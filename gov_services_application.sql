CREATE DATABASE  IF NOT EXISTS `gov_services` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `gov_services`;
-- MySQL dump 10.13  Distrib 5.6.11, for Win32 (x86)
--
-- Host: localhost    Database: gov_services
-- ------------------------------------------------------
-- Server version	5.6.13

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `application`
--

DROP TABLE IF EXISTS `application`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `application` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_id` varchar(200) NOT NULL,
  `service_id` int(11) NOT NULL,
  `service_name` varchar(255) DEFAULT NULL,
  `name` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `mobile` varchar(45) DEFAULT NULL,
  `total_amount` varchar(45) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'Received',
  `document` varchar(255) DEFAULT NULL,
  `document_path` varchar(255) DEFAULT NULL,
  `payment_status` varchar(45) DEFAULT 'Paid',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `razorpay_order_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_id_UNIQUE` (`app_id`),
  KEY `service_id` (`service_id`),
  CONSTRAINT `application_ibfk_2` FOREIGN KEY (`service_id`) REFERENCES `service` (`service_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `application`
--

LOCK TABLES `application` WRITE;
/*!40000 ALTER TABLE `application` DISABLE KEYS */;
INSERT INTO `application` VALUES (1,'APP-1598',2,'Aadhaar Card','xyz','xyz@gmail.com','123456','350.00','Completed',NULL,'documents\\APP-1001_receipt.pdf','Paid','2025-11-06 14:15:30',NULL),(2,'APP-8521',2,'Aadhaar Card','abs','abs@gmail.com','12345','350.00','Received',NULL,NULL,'Paid','2025-11-07 10:37:21',NULL),(3,'APP-3934',2,'Aadhaar Card','Krishi','krishi@gmail.com','123456','350.00','Received',NULL,NULL,'Paid','2025-11-09 17:46:00',NULL),(12,'APP-7036',12,'Income Certificate','Krish','krish@gmail.com','123456','2500.00','Received',NULL,NULL,'Paid','2025-11-10 12:51:07',NULL),(13,'APP-2365',12,'Income Certificate','qwerty','qwerty@gmail.com','12345','2500.00','Received',NULL,NULL,'Paid','2025-11-10 12:55:32',NULL),(14,'APP-7800',1,'Pan Card','Mayank ','nobo33961@gmail.com','8169421990','300.00','Received',NULL,NULL,'Paid','2025-11-10 13:56:23',NULL);
/*!40000 ALTER TABLE `application` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-10 21:21:27
