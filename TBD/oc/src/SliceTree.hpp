#ifndef SliceTree_hpp
#define SliceTree_hpp

#include "SlicedPolygon.hpp"

class Slice
{
	public:

		// Slice(Real, Real);
		Slice(Real, Real, const std::vector<Edge> &, const std::vector<int> &, int);
        Slice(Real, Real, const std::vector<Edge> &,int);

		void contains(const std::vector<Edge> &,const std::vector<int> &);
        void contains(const std::vector<Edge> &);
		bool contains(Edge);

        // Setters
        void setLeft(Slice* left);
        void setRight(Slice* right);

        // Getters
        Slice* getLeft();
        Slice* getRight();
        std::vector<int> getContained();
        Real getBound1();
        Real getBound2();
        int getLevel();
        
        bool isSaturated();
	
	protected:

		Real bound1;
		Real bound2;
		Real mid;

        // Level in tree of slice
        int level;
        bool saturated;

		// Child pointers
		Slice* left;
		Slice* right;
		// Array of indices
		std::vector<int> contained;

};

class SliceTree : public Preprocessor
{
	public:

		SliceTree(const std::vector<Edge> &,Real,Real);
        ~SliceTree();
        void deleteTree(Slice*);

        virtual void preprocess();
        void grow(Slice*);
        std::vector<int> getEdges(AnglePair query);

	protected:

        // Vector of contained edges
		std::vector<Edge> edges;
        Real crit1;
        Real crit2;

		// Root of slice tree
		Slice* root;

        // Height of slice tree
        int height;
};

#endif /* SliceTree_hpp */