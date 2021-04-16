#include "SlicedPolygon.hpp"
#include "SliceTree.hpp"
#include <gtest/gtest.h>

class Poly_04 : public ::testing::Test {

	protected:

	void SetUp() override 
	{
		int numElements = 4;
		std::vector<AnglePair> polygon(numElements);
		AnglePair contained = {1.099557429,0.0};
		
        // Initialize clock angles
        polygon[0][1] = 0.0;
        polygon[1][1] = 1.570796327;
        polygon[2][1] = 4.71238898;
        polygon[3][1] = 0.0;

        // Initialize cone angles
        polygon[0][0] = 1.256637061;
        polygon[1][0] = 0.9424777961;
        polygon[2][0] = 0.6283185307;
        polygon[3][0] = 1.256637061;
		
		grapefruit = new SlicedPolygon(polygon,contained);
		sliceTree = new SliceTree(grapefruit->getEdgeArray(),1,16);
		sliceTree->preprocess();
        grapefruit->addPreprocessor(sliceTree);
	}

  	void TearDown() override 
  	{
  		delete(grapefruit);
		delete(sliceTree);
  	}

	Real tol = .00000001;
	SlicedPolygon* grapefruit;
	Preprocessor* sliceTree;
};

TEST_F(Poly_04,Query_01_numCrossings)
{
    // Test 1: Inside, arbitrary point
	int expectedCrossings = 0;
	AnglePair query = {0.04908738521,4.71238898};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

TEST_F(Poly_04,Query_02_numCrossings)
{
    // Test 2: Inside, arbitrary point
	int expectedCrossings = 0;
	AnglePair query = {0.09817477042,4.71238898};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

TEST_F(Poly_04,Query_03_numCrossings)
{
    // Test 3: Outside, arbitrary point
	int expectedCrossings = 1;
	AnglePair query = {1.256637061,1.570796327};
	int crossings = grapefruit->numCrossings(query);
	ASSERT_EQ(expectedCrossings,crossings);
}

int main(int argc, char **argv)
{
	testing::InitGoogleTest(&argc,argv);
	return RUN_ALL_TESTS();
}
