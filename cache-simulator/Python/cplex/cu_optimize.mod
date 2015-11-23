
int Capacity = 100;
int k = 2;   // Number of items
int n = 5;  // Number of values
range values = 1..n;
range items = 1..k;

// parameters
int p[items][values] = [[ 5, 10, 20, 20, 20],
	                [ 5, 20, 25, 30, 40]];
int w[values] = [ 10, 20, 50, 70, 80];


// decision variable x[j]=1 if the jth item is selected
dvar boolean x[items][values];

// objective function
maximize sum(i in items) max(j in values) x[i][j] * p[i][j];

// constraints
subject to{

sum(i in items) max(j in values) x[i][j] * w[j] <= Capacity;

}
