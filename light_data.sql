-- phpMyAdmin SQL Dump
-- version 4.6.4
-- https://www.phpmyadmin.net/
--
-- 主機: 127.0.0.1
-- 產生時間： 2017-07-04 13:47:38
-- 伺服器版本: 5.7.14
-- PHP 版本： 5.6.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `ogame_data`
--

-- --------------------------------------------------------

--
-- 資料表結構 `light_data`
--

CREATE TABLE `light_data` (
  `Ogame_Clock` varchar(50) COLLATE utf8_bin NOT NULL,
  `userID` varchar(20) COLLATE utf8_bin NOT NULL,
  `galaxy` varchar(1) COLLATE utf8_bin NOT NULL,
  `system` varchar(3) COLLATE utf8_bin NOT NULL,
  `position` varchar(2) COLLATE utf8_bin NOT NULL,
  `moon_min` int(2) NOT NULL,
  `planet_min` int(2) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- 已匯出資料表的索引
--

--
-- 資料表索引 `light_data`
--
ALTER TABLE `light_data`
  ADD PRIMARY KEY (`Ogame_Clock`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
