#include "SlicedPolygon.hpp"
#include "SliceTree.hpp"
#include <gtest/gtest.h>

class Poly_03 : public ::testing::Test {

	protected:

	void SetUp() override 
	{
		int numElements = 5;
		std::vector<AnglePair> polygon(numElements);
		AnglePair contained = {0,0};
		
        // Initialize cone angles
        for (int i = 0; i < numElements; i++)
            polygon[i][0] = 0.7853981634;

        // Initialize clock angles
        polygon[0][1] = 0.7853981634;
        polygon[1][1] = 2.35619449;
        polygon[2][1] = 3.926990817;
        polygon[3][1] = 5.497787144;
        polygon[4][1] = 0.7853981634;
		
		grapefruit = new SlicedPolygon(polygon,contained);
		sliceTree = new SliceTree(grapefruit->getEdgeArray(),1,16);
		sliceTree->preprocess();
        grapefruit->addPreprocessor(sliceTree);
	}

  	void TearDown() override 
  	{
  		delete(grapefruit);
  	}

	Real tol = .00000001;
	SlicedPolygon* grapefruit;
	Preprocessor* sliceTree;
};

TEST_F(Poly_03,Query_01_numCrossings)
{
    // Test 1: Inside, lies along z-axis 
	int expectedCrossings = 0;
	AnglePair query = {0.0,0.0};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

TEST_F(Poly_03,Query_03_numCrossings)
{
    // Test 3: Inside, lies at same clock angle as one of the polygon points (starting point).
	int expectedCrossings = 0;
	AnglePair query = {0.6283185307,0.7853981634};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

TEST_F(Poly_03,Query_04_numCrossings)
{
    // Test 4: Outside, lies at same clock angle as one of the polygon points (starting point).
	int expectedCrossings = 1;
	AnglePair query = {1.047197551,0.7853981634};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

TEST_F(Poly_03,Query_05_numCrossings)
{
    // Test 5: Inside, lies along the middle (clock angle) of a segment.
	int expectedCrossings = 0;
	AnglePair query = {0.3141592654,1.570796327};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

TEST_F(Poly_03,Query_06_numCrossings)
{
    // Test 5: Outside, lies along the middle (clock angle) of a segment.
	int expectedCrossings = 1;
	AnglePair query = {1.047197551,1.570796327};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

int main(int argc, char **argv)
{
	testing::InitGoogleTest(&argc,argv);
	return RUN_ALL_TESTS();
}
