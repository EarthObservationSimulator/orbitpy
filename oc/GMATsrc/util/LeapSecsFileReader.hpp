#ifndef LeapSecsFileReader_hpp
#define LeapSecsFileReader_hpp

#include "utildefs.hpp"
#include "TimeTypes.hpp"

/** 
 * Structure defining internal leap second information.
 *
 * Moved here from inside of the LeapSecsFileReader class to clean up import/
 * export issues with Visual Studio
 */
struct LeapSecondInformation
{
   Real julianDate;         // arg: 2/1/05 assumed to be utc
   Real taiMJD;
   Real offset1;
   Real offset2;
   Real offset3;
};    

class GMATUTIL_API LeapSecsFileReader
{
public:
   LeapSecsFileReader(const std::string &fileName = "tai-utc.dat");
   virtual ~LeapSecsFileReader();
   LeapSecsFileReader(const LeapSecsFileReader& lsfr);
   LeapSecsFileReader& operator=(const LeapSecsFileReader& lsfr);
   
   bool Initialize();
   Real NumberOfLeapSecondsFrom(UtcMjd utcMjd);
   Real GetFirstLeapSecondMJD(Real fromUtcMjd, Real toUtcMjd);
   
   /// Determines whether or not the input time (in TAI MJD, referenced to
   /// GmatTimeConstants::JD_MJD_OFFSET) is in a leap second
   bool IsInLeapSecond(Real theTaiMjd);
   
private:

   bool Parse(std::string line);

   // member data
   bool isInitialized;
   std::vector<LeapSecondInformation> lookUpTable;
   std::string withFileName;
};

#endif // LeapSecsFileReader_hpp
