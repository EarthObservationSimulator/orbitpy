#include <iostream>
#include <string>
#include <ctime>
#include <cmath>
#include <tuple>
#include "AbsoluteDate.hpp"
#include <gtest/gtest.h>

// Parameterized tests for Gregorian to Julian Date conversion 
class GregorianToJulianTestFixture: public testing::TestWithParam<std::tuple<int, int, int, int, int, double, double>>{
   public:
   protected:
      AbsoluteDate date;
};
TEST_P(GregorianToJulianTestFixture, G2JConversionWorks){

   std::tuple<int, int, int, int, int, double, double> param = GetParam();
   int year = std::get<0>(param);
   int month = std::get<1>(param);
   int day = std::get<2>(param);
   int hour = std::get<3>(param);
   int min = std::get<4>(param);
   double sec = std::get<5>(param);
   Real truthDate = std::get<6>(param);

   double tolerance = (1.0/86400)*(1/100); // 1/100th of a second absolute tolerance

   // Set the Gregorian date and test conversion to Julian Date
   date.SetGregorianDate(year, month, day, hour, min, sec);

   EXPECT_NEAR(date.GetJulianDate(), truthDate, tolerance);
}

// Parameterized tests for Julian date to Gregorian conversion
class JulianToGregorianTestFixture: public testing::TestWithParam<std::tuple<double, int, int, int, int, int, double>>{
   public:
   protected:
      AbsoluteDate date;
};
TEST_P(JulianToGregorianTestFixture, J2GConversionWorks){

   std::tuple<double, int, int, int, int, int, double> param = GetParam();
   double jd = std::get<0>(param);
   int truth_year = std::get<1>(param);
   int truth_month = std::get<2>(param);
   int truth_day = std::get<3>(param);
   int truth_hour = std::get<4>(param);
   int truth_min = std::get<5>(param);
   double truth_sec = std::get<6>(param);

   double tolerance = (1.0/1000); // 1/1000th of a second absolute tolerance

   // Set the julian date and test conversion to Gregorian date
   date.SetJulianDate(jd);
   Rvector6 greg  = date.GetGregorianDate();

   EXPECT_EQ(greg[0], truth_year) << "*** ERROR - gregorian (year) is incorrect!!\n" ;
   EXPECT_EQ(greg[1], truth_month) << "*** ERROR - gregorian (month) is incorrect!!\n" ;
   EXPECT_EQ(greg[2], truth_day) << "*** ERROR - gregorian (day) is incorrect!!\n" ;
   EXPECT_EQ(greg[3], truth_hour) << "*** ERROR - gregorian (hour) is incorrect!!\n" ;
   EXPECT_EQ(greg[4], truth_min) << "*** ERROR - gregorian (minute) is incorrect!!\n" ;
   EXPECT_NEAR(greg[5], truth_sec, tolerance) << "*** ERROR - gregorian (second) is incorrect!!\n" ;
}

// Parameterized tests for advance function
class TimeAdvanceFixture: public testing::TestWithParam<std::tuple<double, double, double>>{
   public:
   protected:
      AbsoluteDate date;
};
TEST_P(TimeAdvanceFixture, AdvanceWorks){

   std::tuple<double, double, double> param = GetParam();
   double jd = std::get<0>(param);
   double step = std::get<1>(param); // in seconds
   double truthDate = std::get<2>(param);

   double tolerance = (1.0/86400)*(1/100); // 1/100th of a second absolute tolerance

   // Set the Gregorian date and test conversion to Julian Date
   date.SetJulianDate(jd);
   date.Advance(step);

   EXPECT_NEAR(date.GetJulianDate(), truthDate, tolerance);
}

INSTANTIATE_TEST_CASE_P(G2J, GregorianToJulianTestFixture, testing::Values( 
      std::make_tuple(2017, 1, 15, 22, 30, 20.111, 27769.4377327662 + 2430000),
      std::make_tuple(2021, 12, 18, 13, 45, 11, 2459567.0730439816),
      std::make_tuple(1990, 5, 7, 3, 21, 56, 2448018.6402314813)
      ));

INSTANTIATE_TEST_CASE_P(J2G, JulianToGregorianTestFixture, testing::Values( 
      std::make_tuple(2457269.123456789, 2015, 9, 3, 14, 57, 46.6665852069856),
      std::make_tuple(2459567.0730439816, 2021, 12, 18, 13, 45, 11),
      std::make_tuple(2448018.6402314813, 1990, 5, 7, 3, 21, 56)
      ));

INSTANTIATE_TEST_CASE_P(TimeAdvance, TimeAdvanceFixture, testing::Values( 
      std::make_tuple(2457269.5, 10, 2457269.5 + 1.157407407407408e-04),
      std::make_tuple(2459567.534, 10000, 2459567.534 + 0.115740740740741),
      std::make_tuple(2448018.005, 0.1, 2448018.005 + 1.157407407407407e-06)
      ));


int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}