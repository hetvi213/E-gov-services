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
-- Table structure for table `service`
--

DROP TABLE IF EXISTS `service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service` (
  `service_id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `short_desc` text,
  `base_price` decimal(10,2) NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `documents` text,
  `image` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`service_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service`
--

LOCK TABLES `service` WRITE;
/*!40000 ALTER TABLE `service` DISABLE KEYS */;
INSERT INTO `service` VALUES (1,'Pan Card','Application for new PAN card',300.00,1,'Aadhar Card','Pan.jpg','2025-08-19 07:06:48'),(2,'Aadhaar Card','Update Aadhaar details',350.00,1,NULL,'Aadhar.jpg','2025-08-19 07:06:48'),(3,'Ration Card','Apply for ration card',1000.00,1,NULL,'Ration.png','2025-08-19 07:06:48'),(4,'Senior Citizen Card','Apply for senior citizen card',500.00,1,NULL,'Senior.jpg','2025-08-19 07:06:48'),(5,'Voter ID Card','Apply for voter ID card',500.00,1,NULL,'Voting.jpg','2025-08-19 07:06:48'),(6,'PassPort','Apply for passport',2000.00,1,NULL,'Passport 2.jpg','2025-08-19 07:06:48'),(7,'Food Licence','Apply for food licence',1000.00,1,NULL,'Food.jpg','2025-08-19 07:06:48'),(8,'Gumasta Licence','Apply for gumasta licence',1000.00,1,NULL,'Gumastha.jpeg','2025-08-19 07:06:48'),(9,'GST Registration','Apply for GST registration',3500.00,1,NULL,'GST 1.jpg','2025-08-19 07:06:48'),(10,'Udyham Registration','Apply for udyham registration',600.00,1,NULL,'Udyam.jpeg','2025-08-19 07:06:48'),(11,'Mariage Certificate','Apply for mariage certificate',4500.00,1,NULL,'Marriage.jpg','2025-08-19 07:06:48'),(12,'Income Certificate','Apply for income certificate',2500.00,1,NULL,'Income.jpg','2025-08-19 07:06:48'),(13,'Domicile Certificate','Apply for domicile certificate',3000.00,1,NULL,'Domicile.jpg','2025-08-19 07:06:48'),(14,'Gazatte','Apply for gazatte',1500.00,1,NULL,'Gazatte.jpg','2025-08-19 07:06:48'),(15,'Advertisement','Apply for advertisement',1200.00,1,NULL,'Ad.jpg','2025-08-19 07:06:48'),(16,'PCC','Apply for PCC',550.00,1,NULL,'PCC.jpg','2025-08-19 07:06:48'),(17,'Partnership Deed','Apply for partnership deed',4500.00,1,NULL,'Partnership Deed.jpg','2025-08-19 07:06:48'),(18,'Name Change in Electricity bill','Apply for name change in electricity bill, gas bill',1000.00,1,NULL,'Bill.jpg','2025-08-19 07:06:48'),(19,'Property Tax','Apply for property tax',4500.00,1,NULL,'Property Tax.jpg','2025-08-19 07:06:48'),(20,'Leave Licence Agreement','Apply for leave licence agreement',3500.00,1,NULL,'LLC.jpg','2025-08-19 07:06:48');
/*!40000 ALTER TABLE `service` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-10 21:21:29
