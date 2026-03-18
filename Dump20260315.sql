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
  `user_id` int(11) DEFAULT NULL,
  `app_id` varchar(200) NOT NULL,
  `service_id` int(11) NOT NULL,
  `service_name` varchar(255) DEFAULT NULL,
  `name` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `mobile` varchar(45) DEFAULT NULL,
  `total_amount` varchar(45) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'Received',
  `upload_text` varchar(255) DEFAULT NULL,
  `uploaded_files` text,
  `reject_reason` text,
  `document_path` varchar(255) DEFAULT NULL,
  `payment_status` varchar(45) DEFAULT 'Paid',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_id_UNIQUE` (`app_id`),
  KEY `service_id` (`service_id`),
  KEY `fk_applications_user` (`user_id`),
  CONSTRAINT `application_ibfk_2` FOREIGN KEY (`service_id`) REFERENCES `service` (`service_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_applications_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `application`
--

LOCK TABLES `application` WRITE;
/*!40000 ALTER TABLE `application` DISABLE KEYS */;
INSERT INTO `application` VALUES (1,3,'APP-7582',3,'Pan Card','Hetvi','hetvi5007@gmail.com','1234567890','300.00','Rejected','abc','APP-7582_Pan_Card_5.jpg','abc',NULL,'Paid','2025-11-17 03:56:10'),(2,1,'APP-7800',3,'Pan Card','Mayakn','nobo33961@gmail.com','8169421990','300.00','Completed','','','aadhar card not submitted','documents/APP-1001.pdf','Paid','2025-11-10 13:56:23'),(3,3,'APP-1842',3,'Pan Card','Hetu','hetvi5007@gmail.com','8169421990','300.00','Verified','abc','APP-1842_Aadhar_Card_5.jpg','Incomplete',NULL,'Paid','2025-11-24 06:06:56'),(4,1,'APP-3184',21,'Ration Card','Maya','nobo33961@gmail.com','8169421990','1000.00','Rejected','','','qwerty',NULL,'Paid','2025-11-25 13:50:56'),(5,3,'APP-7824',2,'Aadhaar Card','Hetvi','hetvi5007@gmail.com','8169421990','350.00','Received','','','mm\r\n',NULL,'Paid','2026-01-12 02:49:10'),(6,1,'APP-3342',1,'PassPort','Mayavi','nobo33961@gmail.com','8169421990','2000.00','Processing','','',NULL,NULL,'Paid','2026-01-15 06:15:49'),(7,1,'APP-3971',1,'PassPort','Krishi','admin@gmail.com','8169421990','2000.00','Completed','hetvi','',NULL,'documents/APP-1001.pdf','Paid','2026-01-15 06:30:05'),(8,1,'APP-3713',1,'PassPort','Hetvi','hetvi5007@gmail.com','8169421990','2000.00','Verified','','APP-3713_Society_No_Objection_Certificate_wallpaper1.jpg',NULL,NULL,'Paid','2026-02-06 12:52:37'),(9,3,'APP-1308',2,'Aadhaar Card','Krishi','admin@gmail.com','8169421990','350.00','Completed','','',NULL,'documents/APP-1001.pdf','Paid','2026-02-06 13:13:38'),(10,3,'APP-5541',2,'Aadhaar Card','Hetvi','hetvi5007@gmail.com','8169421990','350.00','Received','','',NULL,NULL,'Paid','2026-02-06 13:22:39'),(13,3,'APP-2024',1,'PassPort','Hetvi','hetvi5007@gmail.com','8169421990','2000.00','Processing','','APP-2024_Society_No_Objection_Certificate_wallpaper1.jpg',NULL,NULL,'Paid','2026-02-06 13:35:46'),(14,4,'APP-5260',5,'Mariage Certificate','Mayank','mayanksaha95@gmail.com','9821351123','4500.00','Rejected','','APP-5260_Passport_size_photo_4_each_for_both_wallpaper1.jpg','vb',NULL,'Paid','2026-02-06 15:24:18'),(15,3,'APP-6848',1,'PassPort','Hetvi','hetvi5007@gmail.com','8169421990','2000.00','Verified','','APP-6848_Birth_Certificate_Gov_Service.png','d',NULL,'Paid','2026-02-07 05:22:55'),(16,3,'APP-2823',1,'PassPort','Hetvi','hetvi5007@gmail.com','8169421990','2000.00','Processing','','',NULL,NULL,'Paid','2026-02-07 06:56:08'),(18,3,'APP-1718',3,'Pan Card','Hetvi','hetvi5007@gmail.com','9821351123','300.00','Received','vcx','',NULL,NULL,'Paid','2026-03-15 06:43:29'),(19,3,'APP-1197',3,'Pan Card','Hetvi','hetvi5007@gmail.com','8169421990','300.00','Received','bv','APP-1197_Pan_Card_wallpaper3.jpg',NULL,NULL,'Paid','2026-03-15 06:48:31'),(20,3,'APP-6102',21,'Ration Card','Hetvi','hetvi5007@gmail.com','8097272875','1000.00','Received','vc','APP-6102_Aadhar_Card_wallpaper_1.jpg',NULL,NULL,'Paid','2026-03-15 07:02:19');
/*!40000 ALTER TABLE `application` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documents`
--

DROP TABLE IF EXISTS `documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `documents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `application_id` int(11) NOT NULL,
  `owner_user_id` int(11) NOT NULL,
  `stored_filename` varchar(255) NOT NULL,
  `original_filename` varchar(255) DEFAULT NULL,
  `status` varchar(32) DEFAULT 'uploaded',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_application` (`application_id`),
  CONSTRAINT `fk_application` FOREIGN KEY (`application_id`) REFERENCES `application` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documents`
--

LOCK TABLES `documents` WRITE;
/*!40000 ALTER TABLE `documents` DISABLE KEYS */;
/*!40000 ALTER TABLE `documents` ENABLE KEYS */;
UNLOCK TABLES;

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
  `documents` text,
  `image` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_active` int(11) DEFAULT '1',
  PRIMARY KEY (`service_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service`
--

LOCK TABLES `service` WRITE;
/*!40000 ALTER TABLE `service` DISABLE KEYS */;
INSERT INTO `service` VALUES (1,'PassPort','Apply for passport',2000.00,'Birth Certificate, 10th or 12th Marksheet, Pan Card, Bank Passbookor statement with Photo & Bank Stamp, Aadhar Card, Marriage Caertificate orAffidevit, Society No Objection Certificate','Passport 2.jpg','2025-08-19 07:06:48',NULL),(2,'Aadhaar Card','Update Aadhaar details',350.00,NULL,'Aadhar.jpg','2025-08-19 07:06:48',NULL),(3,'Pan Card','Application for new PAN card',300.00,'Aadhar Card, Pan Card','Pan.jpg','2025-08-19 07:06:48',NULL),(4,'Gumasta Licence','Apply for gumasta licence',1000.00,'Shop Agreement/Shop Electicity Bill, Firm name & Type of Business, Mobile No., Email Id, Aadhar Card, Pan Card, 1 Passport Size Photo','Gumastha.jpeg','2025-08-19 07:06:48',NULL),(5,'Mariage Certificate','Apply for mariage certificate',4500.00,'Invitation Card, Wedding or Joint Photo, Passport size photo 4 each for both, Aadhar Card of both, Pan Card of both, Birth or School Leaving Certificate of both, Wife-Ration Card proof with father\'s name or Voting Card or Passport, Husband- Ration Card or Voting Card or Passport, 3 Witness- Pancard, Aadhar Card, Passport size photo 3 each','Marriage.jpg','2025-08-19 07:06:48',NULL),(6,'Domicile Certificate','Apply for domicile certificate',3000.00,'1 Passport Size Photo, Ration Card, Birth Certificate/School Leaving Certificate, Pan Card, Aadhar Card, Last 10 years residence Proof, Student 1st to Till date Marksheets, Guardian\'s Domicile Cetificate compulsory if minor','Domicile.jpg','2025-08-19 07:06:48',NULL),(7,'Income Certificate','Apply for income certificate',2500.00,'Pan Card, Residence & office Address, Bank Statement, Investment Details, Cancel Cheque, Aadhar Card','Income.jpg','2025-08-19 07:06:48',NULL),(8,'Food Licence','Apply for food licence',1000.00,'1 Passport Size colour Photo, Pan Card, Aadhar Card, Agreement (LL), Light Bill, Firm Name, Gumastha Licence','Food.jpg','2025-08-19 07:06:48',NULL),(9,'Udyham Registration','Apply for udyham registration',600.00,'Aadhar Card, Pan Card, Bank A/C no. & IFSC Code, Firm name & type of Business, Mobile No, Email Id','Udyam.jpeg','2025-08-19 07:06:48',NULL),(10,'Gazatte','Apply for gazatte',1500.00,'1 Passport size color Photo, Address Proof (Any 1), Age Proof in Case Minor (Any 1.. Birth/Leaving/Bonofite Certificate), Marriage Certificate Affidavit, Divorce Papers Affidavit','Gazatte.jpg','2025-08-19 07:06:48',NULL),(11,'GST Registration','Apply for GST registration',3500.00,'Pan Card, Aadhar Card, Gumastha Licence, Light Bill, If rented then Owner NOC','GST 1.jpg','2025-08-19 07:06:48',NULL),(12,'PCC','Apply for PCC',550.00,'Company Letter, Aadhar Card, Pan Card,School Leaving or Birth Certificate','PCC.jpg','2025-08-19 07:06:48',NULL),(13,'Senior Citizen Card','Apply for senior citizen card',500.00,'Ration Card or Light Bill, Blood Group Report(If possible), 1 Passport size colour Photo, Pan Card, Aadhhar Card, Passport or Voting Card, School Leaving or Birth Certificate','Senior.jpg','2025-08-19 07:06:48',NULL),(14,'Voter ID Card','Apply for voter ID card',500.00,'Pan Card, Aadhar Card, 1 passport size Photo','Voting.jpg','2025-08-19 07:06:48',NULL),(15,'Leave Licence Agreement','Apply for leave licence agreement',3500.00,'Pan Card, Aadhar Card, 1 Passport size Phot, Owner Tenant, 2 witness- (Aadhar Card, Pan Card)','LLC.jpg','2025-08-19 07:06:48',NULL),(16,'Name Change in Electricity bill','Apply for name change in electricity bill, gas bill',1000.00,'1 Passport size colour Photo, Pan Card, Society NOC, Latest Bill Paid, Agreement, Aadhar Card','Bill.jpg','2025-08-19 07:06:48',NULL),(17,'Partnership Deed','Apply for partnership deed',4500.00,'All Partners- Aadhar Card, 1 Passport size Photo','Partnership Deed.jpg','2025-08-19 07:06:48',NULL),(18,'Advertisement','Apply for advertisement',1200.00,'','Ad.jpg','2025-08-19 07:06:48',NULL),(19,'Name Change in Property Tax','Apply for name change in property tax',4500.00,'Aadhar card, Pan Card, Society NOC, Total Chain Agreement, Last Property Tax Paid Receipt','Property Tax.jpg','2025-08-19 07:06:48',NULL),(20,'Driving Licence','Apply for Driving Licence',2000.00,'2 Passport size colour Photo, Aadhar Card, Ration card, LIC Policy, School Leaving Certificat, BirthCertificate, Light Bill, Registered Rent Agreement or Flat Agreement','Driving.jpg','2025-11-14 14:08:53',NULL),(21,'Ration Card','Apply for ration card',1000.00,'Pan Card, Aadhar Card, Agreement','Ration.png','2025-08-19 07:06:48',NULL);
/*!40000 ALTER TABLE `service` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Mayank','nobo33961@gmail.com','8169421990','scrypt:32768:8:1$1HAgJ2GMao5cej9N$2c16ba64c3841ede8db91bb0e7a0ec6abf7b63f14532510de0eb02fe5dea03e4d8e726662f859d002ac12fc3a9b3bd8261a52052bf3628d60de591259238bda9','2025-11-10 13:52:18'),(2,'Admin','admin@gmail.com','123456789','scrypt:32768:8:1$slZ2DSvhDbGVMLt6$62d86dacb5613e69ddcc53a1ff782f85b75d3bf2ca9c2da24f417c37e59e28b54a7e01ec6b4872c3ed5b6c18d62c7a24fb2200a2e648f4e2bd5d228a9e5a80e2','2025-11-09 13:27:16'),(3,'Hetvi','hetvi5007@gmail.com','8097272875','scrypt:32768:8:1$x8okiwtfISS9Z5TF$c0eb15d3281ae7b8472f44e0e885f0441c7e03085e3b5f6d8a2b7a814b4b91f8ed31b290258202f735a0dddde2114c8331f5d0c6c97bebf461e02627ec4b591f','2025-11-13 11:20:59'),(4,'Mayank Nobo Saha','mayanksaha95@gmail.com','9821351123','scrypt:32768:8:1$T2EcbQjUsZhFgvnm$83e62498e1cb3877b258e3be2f1eb87bc9ef7c42a278e7808c7da7ee3b6054c4f261ed9037370bfa5b1905e508f6a5852a8a99897e1396b757d04b1fc0b867a8','2026-02-06 15:12:09');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'gov_services'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-15 12:38:14
