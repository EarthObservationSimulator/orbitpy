#include "SlicedPolygon.hpp"
#include "SliceArray.hpp"
#include <gtest/gtest.h>
#include <iostream>

class Poly_TN : public ::testing::Test {

	protected:

	void SetUp() override 
	{
		std::vector<AnglePair> TN = util::csvRead("util/Tennessee.csv");
        AnglePair contained = TN.back();
        TN.pop_back();
		
		grapefruit = new SlicedPolygon(TN,contained);
		sliceTree = new SliceArray(grapefruit->getLonArray(),grapefruit->getEdgeArray());
		sliceTree->preprocess();
	}

  	void TearDown() override 
  	{
  		delete(grapefruit);
  	}

	Real tol = .00000001;
	SlicedPolygon* grapefruit;
	Preprocessor* sliceTree;
};

TEST_F(Poly_TN,begin)
{
    AnglePair randomQuery = {1.345,.3457};

    int numBefore = grapefruit->numCrossings(randomQuery);

    grapefruit->addPreprocessor(sliceTree);

    int numAfter = grapefruit->numCrossings(randomQuery);

    ASSERT_EQ(numBefore,numAfter);
}

int main(int argc, char **argv)
{
	testing::InitGoogleTest(&argc,argv);
	return RUN_ALL_TESTS();
}