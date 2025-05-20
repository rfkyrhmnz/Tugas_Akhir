-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 20, 2025 at 05:11 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pengarsipan_surat`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_insert_surat` (IN `p_nomor` VARCHAR(100), IN `p_pengirim` VARCHAR(100), IN `p_tanggal` DATE, IN `p_perihal` VARCHAR(255), IN `p_isi` TEXT, IN `p_file_path` VARCHAR(255), IN `p_kategori` ENUM('Masuk','Keluar'), IN `p_tanggal_arsip` DATETIME, IN `p_user_id` INT, OUT `p_new_id` INT)   BEGIN
    INSERT INTO surat (nomor_surat, pengirim, tanggal_surat, perihal, isi, file_path, kategori, tanggal_arsip, user_id)
    VALUES (p_nomor, p_pengirim, p_tanggal, p_perihal, p_isi, p_file_path, p_kategori, p_tanggal_arsip, p_user_id);
    SET p_new_id = LAST_INSERT_ID();
    
    INSERT INTO riwayat (surat_id, aksi, user_id, waktu)
    VALUES (p_new_id, 'Insert', p_user_id, p_tanggal_arsip);
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `riwayat`
--

CREATE TABLE `riwayat` (
  `id` int(11) NOT NULL,
  `surat_id` int(11) NOT NULL,
  `aksi` enum('Insert','Update','Delete') NOT NULL,
  `user_id` int(11) NOT NULL,
  `waktu` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `riwayat`
--

INSERT INTO `riwayat` (`id`, `surat_id`, `aksi`, `user_id`, `waktu`) VALUES
(37, 15, 'Insert', 3, '2025-05-20 15:12:08'),
(38, 15, 'Update', 3, '2025-05-20 15:12:22');

-- --------------------------------------------------------

--
-- Table structure for table `surat`
--

CREATE TABLE `surat` (
  `id` int(11) NOT NULL,
  `nomor_surat` varchar(100) NOT NULL,
  `pengirim` varchar(100) NOT NULL,
  `tanggal_surat` date NOT NULL,
  `perihal` varchar(255) NOT NULL,
  `isi` text NOT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `kategori` enum('Masuk','Keluar') NOT NULL,
  `tanggal_arsip` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `status_arsip` enum('Aktif','Arsip') DEFAULT 'Aktif'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `surat`
--

INSERT INTO `surat` (`id`, `nomor_surat`, `pengirim`, `tanggal_surat`, `perihal`, `isi`, `file_path`, `kategori`, `tanggal_arsip`, `user_id`, `status_arsip`) VALUES
(9, '1', 'Kyy', '2025-08-24', 'Izin', 'P', NULL, 'Masuk', '2025-05-20 11:34:14', 3, 'Arsip'),
(10, '12', 'Kyy', '2005-09-25', 'Izin', 'Alasan jir', NULL, 'Keluar', '2025-05-20 11:46:16', 3, 'Arsip'),
(11, '123', 'Kyy', '2025-08-23', 'Izin', 'Izin Sakit', NULL, 'Masuk', '2025-05-20 12:29:02', 3, 'Arsip'),
(12, '1', 'Kyy', '2006-09-23', 'Izin', 'Izin', NULL, 'Masuk', '2025-05-20 13:06:36', 3, 'Arsip'),
(13, '14', 'Kyy', '2005-09-23', 'Izin', 'Izin', NULL, 'Masuk', '2025-05-20 13:14:08', 3, 'Arsip'),
(14, '12', 'Jarwo', '2045-09-12', 'Peringatan Maulid Nabi', 'JIR', NULL, 'Masuk', '2025-05-20 13:52:41', 1, 'Arsip'),
(15, '12', 'Kyy', '2008-12-05', 'Izin', 'p', NULL, 'Masuk', '2025-05-20 15:12:08', 3, 'Aktif');

--
-- Triggers `surat`
--
DELIMITER $$
CREATE TRIGGER `trg_after_delete_surat` AFTER DELETE ON `surat` FOR EACH ROW BEGIN
    INSERT INTO riwayat (surat_id, aksi, user_id, waktu)
    VALUES (OLD.id, 'Delete', OLD.user_id, NOW());
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('Admin','User') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password_hash`, `role`) VALUES
(1, 'admin', '$2y$10$gRo9hskt01llWNMPNhFGW.TLvjsqVEk1uGQTgdBgqHa45M4wLhuXK', 'Admin'),
(3, 'Kyy', '$2b$12$foDfCiZs0jyD8tVmOv7QbezS21RT9I0UUYAMLsh3yoMCLJlE/rw1y', 'User'),
(5, 'Jarwo', '$2b$12$gK8nwhlW3M7nZqCGPcdE7.X1yaTWeXuZdOruSpp7MVZI.awcNnbG6', 'Admin'),
(6, 'Rafly', '$2b$12$2Ioj0t.BrOC27sB9nKisou7rpFhJRIYQKPjl4wKukIx30QpmHf3Eu', 'Admin'),
(7, 'ASA', '$2b$12$EhIp6zMrXQeUokyZXVOgmeNWIz79Hf/2TJ51HA4pne4npdmvpeFxS', 'User');

-- --------------------------------------------------------

--
-- Stand-in structure for view `view_surat_aktif`
-- (See below for the actual view)
--
CREATE TABLE `view_surat_aktif` (
`id` int(11)
,`nomor_surat` varchar(100)
,`pengirim` varchar(100)
,`tanggal_surat` date
,`perihal` varchar(255)
,`kategori` enum('Masuk','Keluar')
,`username` varchar(50)
,`file_path` varchar(255)
,`user_id` int(11)
);

-- --------------------------------------------------------

--
-- Structure for view `view_surat_aktif`
--
DROP TABLE IF EXISTS `view_surat_aktif`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `view_surat_aktif`  AS SELECT `s`.`id` AS `id`, `s`.`nomor_surat` AS `nomor_surat`, `s`.`pengirim` AS `pengirim`, `s`.`tanggal_surat` AS `tanggal_surat`, `s`.`perihal` AS `perihal`, `s`.`kategori` AS `kategori`, `u`.`username` AS `username`, `s`.`file_path` AS `file_path`, `s`.`user_id` AS `user_id` FROM (`surat` `s` join `users` `u` on(`s`.`user_id` = `u`.`id`)) WHERE `s`.`status_arsip` = 'Aktif' ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `riwayat`
--
ALTER TABLE `riwayat`
  ADD PRIMARY KEY (`id`),
  ADD KEY `surat_id` (`surat_id`),
  ADD KEY `fk_riwayat_user_delete` (`user_id`);

--
-- Indexes for table `surat`
--
ALTER TABLE `surat`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_surat_user_delete` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `riwayat`
--
ALTER TABLE `riwayat`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

--
-- AUTO_INCREMENT for table `surat`
--
ALTER TABLE `surat`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `riwayat`
--
ALTER TABLE `riwayat`
  ADD CONSTRAINT `fk_riwayat_user_delete` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `riwayat_ibfk_1` FOREIGN KEY (`surat_id`) REFERENCES `surat` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `surat`
--
ALTER TABLE `surat`
  ADD CONSTRAINT `fk_surat_user_delete` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
